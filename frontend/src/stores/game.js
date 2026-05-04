import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { newGame, sendAction, sendCombatAction, sendNPCAction } from '../api/game'

export const useGameStore = defineStore('game', () => {
  const sessionId = ref(null)
  const messages = ref([])
  const choices = ref([])
  const state = ref({
    hp: 100, max_hp: 100, location: 'unknown', inventory: [],
    combat: { active: false, enemy: {}, round_num: 0, log: [] },
    npc: { active: false, npc: {}, dialogue: [] },
    quest: { stage: 'undiscovered', title: '诅咒小镇的秘密', description: '', clues_found: [], has_treasure: false, boss_defeated: false },
    game_over: false, victory: false,
  })
  const loading = ref(false)
  const gameOver = computed(() => state.value.game_over || state.value.hp <= 0)
  const victory = computed(() => state.value.victory)
  const inCombat = computed(() => state.value.combat?.active)
  const inDialogue = computed(() => state.value.npc?.active)
  const encounter = ref({ type: 'none' })

  function resetState() {
    messages.value = []
    choices.value = []
    encounter.value = { type: 'none' }
    state.value = {
      hp: 100, max_hp: 100, location: 'unknown', inventory: [],
      combat: { active: false, enemy: {}, round_num: 0, log: [] },
      npc: { active: false, npc: {}, dialogue: [] },
      quest: { stage: 'undiscovered', title: '诅咒小镇的秘密', description: '', clues_found: [], has_treasure: false, boss_defeated: false },
      game_over: false, victory: false,
    }
  }

  async function startGame() {
    loading.value = true
    resetState()
    try {
      const data = await newGame()
      sessionId.value = data.session_id
      state.value = data.state
      messages.value.push({ role: 'narrator', text: data.narrative })
      choices.value = data.choices || []
      encounter.value = data.encounter || { type: 'none' }
    } catch (e) {
      messages.value.push({ role: 'system', text: '连接失败，请检查后端服务是否启动。' })
    } finally {
      loading.value = false
    }
  }

  async function doAction(action) {
    if (loading.value || gameOver.value) return
    loading.value = true
    messages.value.push({ role: 'player', text: action })
    choices.value = []
    try {
      const data = await sendAction(sessionId.value, action)
      state.value = data.state
      messages.value.push({ role: 'narrator', text: data.narrative })
      choices.value = data.choices || []
      encounter.value = data.encounter || { type: 'none' }
    } catch (e) {
      messages.value.push({ role: 'system', text: '请求失败，请重试。' })
    } finally {
      loading.value = false
    }
  }

  async function doCombatAction(tactic) {
    if (loading.value || !inCombat.value) return
    loading.value = true
    choices.value = []
    try {
      const data = await sendCombatAction(sessionId.value, tactic)
      state.value = data.state
      const cr = data.combat_result
      // 将骰子结果和战斗描述一起显示
      let combatText = data.narrative
      if (cr) {
        combatText = `🎲 掷骰: ${cr.dice_roll} (修正后 ${cr.effective_roll}) | ${cr.tactic}\n${cr.description}\n\n${data.narrative}`
      }
      messages.value.push({ role: 'combat', text: combatText })
      choices.value = data.choices || []
      if (cr?.combat_ended) {
        if (cr.result === 'victory') {
          messages.value.push({ role: 'system', text: `战斗胜利！击败了 ${cr.enemy_defeated}！` })
        } else if (cr.result === 'defeat') {
          messages.value.push({ role: 'system', text: '你被击败了……' })
        } else if (cr.result === 'escaped') {
          messages.value.push({ role: 'system', text: '成功逃离了战斗！' })
        }
      }
    } catch (e) {
      messages.value.push({ role: 'system', text: '战斗请求失败，请重试。' })
    } finally {
      loading.value = false
    }
  }

  async function doNPCAction(action) {
    if (loading.value || !inDialogue.value) return
    loading.value = true
    choices.value = []
    try {
      const data = await sendNPCAction(sessionId.value, action)
      state.value = data.state
      messages.value.push({ role: 'narrator', text: data.narrative })
      choices.value = data.choices || []
    } catch (e) {
      messages.value.push({ role: 'system', text: '对话请求失败，请重试。' })
    } finally {
      loading.value = false
    }
  }

  return {
    sessionId, messages, choices, state, loading, gameOver, victory,
    inCombat, inDialogue, encounter,
    startGame, doAction, doCombatAction, doNPCAction,
  }
})

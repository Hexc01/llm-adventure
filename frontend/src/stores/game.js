import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { newGame, sendAction } from '../api/game'

export const useGameStore = defineStore('game', () => {
  const sessionId = ref(null)
  const messages = ref([])
  const choices = ref([])
  const state = ref({ hp: 100, max_hp: 100, location: 'unknown', inventory: [] })
  const loading = ref(false)
  const gameOver = computed(() => state.value.hp <= 0)

  async function startGame() {
    loading.value = true
    messages.value = []
    choices.value = []
    try {
      const data = await newGame()
      sessionId.value = data.session_id
      state.value = data.state
      messages.value.push({ role: 'narrator', text: data.narrative })
      choices.value = data.choices || []
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
    } catch (e) {
      messages.value.push({ role: 'system', text: '请求失败，请重试。' })
    } finally {
      loading.value = false
    }
  }

  return { sessionId, messages, choices, state, loading, gameOver, startGame, doAction }
})

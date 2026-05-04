<template>
  <div v-if="game.inCombat" class="combat-panel">
    <div class="combat-header">
      <span class="combat-icon">⚔️</span>
      <h3>战斗中</h3>
    </div>

    <div class="enemy-info">
      <div class="enemy-name">{{ enemy.name }}</div>
      <div class="enemy-desc">{{ enemy.description }}</div>
      <div class="enemy-stats">
        <div class="stat-row">
          <span class="label">生命</span>
          <div class="hp-bar enemy-hp">
            <div class="hp-fill" :style="{ width: enemyHpPercent + '%' }"></div>
          </div>
          <span class="value">{{ enemy.hp }}/{{ enemy.max_hp }}</span>
        </div>
        <div class="stat-row">
          <span class="label">难度</span>
          <span class="value difficulty" :class="difficultyClass">{{ enemy.difficulty }}</span>
        </div>
        <div class="stat-row">
          <span class="label">回合</span>
          <span class="value">{{ combat.round_num }}</span>
        </div>
      </div>
    </div>

    <div class="combat-actions">
      <div class="action-row">
        <button
          v-for="action in combatActions"
          :key="action.id"
          class="btn-combat"
          :class="action.class"
          @click="game.doCombatAction(action.id)"
          :disabled="game.loading"
        >
          <span class="action-name">{{ action.name }}</span>
          <span class="action-desc">{{ action.desc }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()

const enemy = computed(() => game.state.combat?.enemy || {})
const combat = computed(() => game.state.combat || {})

const enemyHpPercent = computed(() => {
  const e = enemy.value
  if (!e.max_hp) return 0
  return (e.hp / e.max_hp) * 100
})

const difficultyClass = computed(() => {
  const d = enemy.value.difficulty || 0
  if (d >= 16) return 'diff-extreme'
  if (d >= 12) return 'diff-hard'
  if (d >= 8) return 'diff-medium'
  return 'diff-easy'
})

const combatActions = [
  { id: 'attack', name: '攻击', desc: '修正 +0', class: 'action-normal' },
  { id: 'heavy_attack', name: '全力一击', desc: '修正 -3, 伤害x1.8', class: 'action-risky' },
  { id: 'defend', name: '防御反击', desc: '修正 +5, 伤害x0.6', class: 'action-safe' },
  { id: 'magic', name: '魔法攻击', desc: '修正 -2, 伤害x1.5', class: 'action-magic' },
  { id: 'dodge', name: '闪避', desc: '修正 +4, 受伤x0.3', class: 'action-safe' },
  { id: 'flee', name: '逃跑', desc: '修正 +6', class: 'action-flee' },
]
</script>

<style scoped>
.combat-panel {
  background: #1a0a0a;
  border: 1px solid #4a1a1a;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.combat-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.combat-header h3 {
  color: #ff6a6a;
  font-size: 1.1rem;
}

.combat-icon {
  font-size: 1.3rem;
}

.enemy-info {
  background: #0f0f18;
  padding: 12px;
  border-radius: 6px;
}

.enemy-name {
  font-size: 1.1rem;
  color: #ff9a6a;
  font-weight: bold;
  margin-bottom: 4px;
}

.enemy-desc {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 8px;
}

.enemy-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 0.8rem;
  color: #666;
  min-width: 32px;
}

.value {
  font-size: 0.9rem;
  color: #d4c8a8;
}

.difficulty {
  font-weight: bold;
}

.diff-easy { color: #4caf50; }
.diff-medium { color: #ff9800; }
.diff-hard { color: #f44336; }
.diff-extreme { color: #ff1744; }

.hp-bar {
  flex: 1;
  height: 8px;
  background: #1a1a25;
  border-radius: 4px;
  overflow: hidden;
}

.hp-fill {
  height: 100%;
  background: #f44336;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.enemy-hp .hp-fill {
  background: linear-gradient(90deg, #ff4444, #ff6a6a);
}

.combat-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.btn-combat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 8px;
  border: 1px solid #3a3a4a;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Noto Serif SC', serif;
}

.btn-combat:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-combat:hover:not(:disabled) {
  transform: translateY(-1px);
}

.action-name {
  font-size: 0.9rem;
  font-weight: bold;
}

.action-desc {
  font-size: 0.7rem;
  opacity: 0.7;
}

.action-normal {
  background: #1a1a25;
  color: #d4c8a8;
}
.action-normal:hover:not(:disabled) {
  border-color: #d4c8a8;
  background: #252535;
}

.action-risky {
  background: #2a1515;
  color: #ff6a6a;
}
.action-risky:hover:not(:disabled) {
  border-color: #ff6a6a;
  background: #3a1a1a;
}

.action-safe {
  background: #152a15;
  color: #6aff6a;
}
.action-safe:hover:not(:disabled) {
  border-color: #6aff6a;
  background: #1a3a1a;
}

.action-magic {
  background: #15152a;
  color: #6a8aff;
}
.action-magic:hover:not(:disabled) {
  border-color: #6a8aff;
  background: #1a1a3a;
}

.action-flee {
  background: #2a2a15;
  color: #d4c8a8;
}
.action-flee:hover:not(:disabled) {
  border-color: #d4c8a8;
  background: #3a3a1a;
}

@media (max-width: 600px) {
  .action-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

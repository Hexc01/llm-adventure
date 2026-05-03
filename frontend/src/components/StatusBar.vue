<template>
  <div class="status-bar">
    <div class="stat">
      <span class="label">生命</span>
      <div class="hp-bar">
        <div class="hp-fill" :style="{ width: hpPercent + '%' }" :class="hpClass"></div>
      </div>
      <span class="value">{{ game.state.hp }}/{{ game.state.max_hp }}</span>
    </div>
    <div class="stat">
      <span class="label">位置</span>
      <span class="value">{{ game.state.location }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()

const hpPercent = computed(() => (game.state.hp / game.state.max_hp) * 100)
const hpClass = computed(() => {
  if (hpPercent.value > 60) return 'hp-high'
  if (hpPercent.value > 30) return 'hp-mid'
  return 'hp-low'
})
</script>

<style scoped>
.status-bar {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #111118;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
}

.stat {
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

.hp-bar {
  width: 120px;
  height: 8px;
  background: #1a1a25;
  border-radius: 4px;
  overflow: hidden;
}

.hp-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.hp-high {
  background: #4caf50;
}

.hp-mid {
  background: #ff9800;
}

.hp-low {
  background: #f44336;
}
</style>

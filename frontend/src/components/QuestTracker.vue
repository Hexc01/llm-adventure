<template>
  <div v-if="quest.stage !== 'undiscovered'" class="quest-tracker">
    <div class="quest-header">
      <span class="quest-icon">📜</span>
      <span class="quest-title">{{ quest.title }}</span>
    </div>

    <div class="quest-desc">{{ quest.description }}</div>

    <div class="quest-progress">
      <div
        v-for="(stage, i) in stages"
        :key="stage.id"
        class="stage"
        :class="stageClass(stage.id, i)"
      >
        <span class="stage-dot"></span>
        <span class="stage-name">{{ stage.name }}</span>
      </div>
    </div>

    <div v-if="quest.has_treasure" class="treasure-badge">
      已获得宝藏！逃离小镇即可胜利！
    </div>
    <div v-if="quest.boss_defeated && !quest.has_treasure" class="boss-badge">
      Boss已被击败！去拿宝藏吧！
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()
const quest = computed(() => game.state.quest || {})

const stages = [
  { id: 'undiscovered', name: '未知' },
  { id: 'rumor', name: '传闻' },
  { id: 'clues', name: '线索' },
  { id: 'lair', name: '巢穴' },
  { id: 'boss', name: '讨伐' },
  { id: 'treasure', name: '宝藏' },
  { id: 'escape', name: '逃离' },
]

const stageOrder = ['undiscovered', 'rumor', 'clues', 'lair', 'boss', 'treasure', 'escape', 'victory']

function stageClass(stageId, index) {
  const currentIdx = stageOrder.indexOf(quest.value.stage)
  const stageIdx = stageOrder.indexOf(stageId)
  if (stageIdx < currentIdx) return 'completed'
  if (stageIdx === currentIdx) return 'current'
  return 'pending'
}
</script>

<style scoped>
.quest-tracker {
  background: #111818;
  border: 1px solid #2a3a2a;
  border-radius: 8px;
  padding: 12px 16px;
}

.quest-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.quest-icon {
  font-size: 1.1rem;
}

.quest-title {
  color: #c9a84c;
  font-size: 0.95rem;
  font-weight: bold;
}

.quest-desc {
  color: #8a8070;
  font-size: 0.8rem;
  margin-bottom: 10px;
}

.quest-progress {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.stage {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
}

.stage-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s;
}

.stage.completed .stage-dot {
  background: #4caf50;
}

.stage.current .stage-dot {
  background: #c9a84c;
  box-shadow: 0 0 6px rgba(201, 168, 76, 0.6);
}

.stage.pending .stage-dot {
  background: #333;
}

.stage.completed .stage-name {
  color: #4caf50;
}

.stage.current .stage-name {
  color: #c9a84c;
  font-weight: bold;
}

.stage.pending .stage-name {
  color: #444;
}

.treasure-badge,
.boss-badge {
  margin-top: 8px;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  text-align: center;
}

.treasure-badge {
  background: #2a2a15;
  color: #c9a84c;
  border: 1px solid #c9a84c;
}

.boss-badge {
  background: #152a15;
  color: #4caf50;
  border: 1px solid #4caf50;
}
</style>

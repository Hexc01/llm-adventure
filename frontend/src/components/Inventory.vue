<template>
  <div v-if="game.state.inventory.length > 0" class="inventory">
    <span class="label">物品栏</span>
    <div class="items">
      <span v-for="(item, i) in game.state.inventory" :key="i" class="item">
        {{ item }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { useGameStore } from '../stores/game'
const game = useGameStore()
</script>

<style scoped>
.inventory {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: #111118;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
}

.label {
  font-size: 0.8rem;
  color: #666;
  min-width: 48px;
}

.items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.item {
  background: #1a1a25;
  border: 1px solid #3a3a4a;
  padding: 4px 12px;
  font-size: 0.85rem;
  border-radius: 4px;
  color: #c9a84c;
}
</style>

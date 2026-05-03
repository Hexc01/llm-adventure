<template>
  <div v-if="game.choices.length > 0 || !game.gameOver" class="choice-panel">
    <div v-if="game.choices.length > 0" class="choices">
      <button
        v-for="(choice, i) in game.choices"
        :key="i"
        class="btn-choice"
        @click="game.doAction(choice)"
        :disabled="game.loading"
      >
        {{ choice }}
      </button>
    </div>
    <div class="custom-action">
      <input
        v-model="customInput"
        @keydown.enter="submitCustom"
        placeholder="输入你的行动..."
        :disabled="game.loading || game.gameOver"
      />
      <button class="btn-send" @click="submitCustom" :disabled="game.loading || game.gameOver || !customInput.trim()">
        发送
      </button>
    </div>
    <div v-if="game.gameOver" class="game-over">
      <p>你的冒险结束了……</p>
      <button class="btn-primary" @click="game.startGame">重新开始</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()
const customInput = ref('')

function submitCustom() {
  const text = customInput.value.trim()
  if (!text || game.loading || game.gameOver) return
  game.doAction(text)
  customInput.value = ''
}
</script>

<style scoped>
.choice-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.choices {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn-choice {
  background: #1a1a25;
  color: #c9a84c;
  border: 1px solid #3a3a4a;
  padding: 10px 18px;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.9rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-choice:hover:not(:disabled) {
  background: #252535;
  border-color: #c9a84c;
}

.btn-choice:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.custom-action {
  display: flex;
  gap: 8px;
}

.custom-action input {
  flex: 1;
  background: #111118;
  color: #d4c8a8;
  border: 1px solid #2a2a3a;
  padding: 12px 16px;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}

.custom-action input:focus {
  border-color: #c9a84c;
}

.custom-action input::placeholder {
  color: #444;
}

.btn-send {
  background: #c9a84c;
  color: #0a0a0f;
  border: none;
  padding: 12px 24px;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.game-over {
  text-align: center;
  padding: 20px;
  background: #1a0a0a;
  border: 1px solid #4a1a1a;
  border-radius: 8px;
}

.game-over p {
  color: #ff6a6a;
  font-size: 1.2rem;
  margin-bottom: 16px;
}
</style>

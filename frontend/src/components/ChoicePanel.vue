<template>
  <div class="choice-panel">
    <!-- 普通选项（不在战斗/对话中时显示） -->
    <div v-if="!game.inCombat && !game.inDialogue && !game.gameOver && game.choices.length > 0" class="choices">
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

    <!-- 自定义行动输入（战斗/对话/gameover时不显示） -->
    <div v-if="!game.inCombat && !game.inDialogue && !game.gameOver" class="custom-action">
      <input
        v-model="customInput"
        @keydown.enter="submitCustom"
        placeholder="输入你的行动..."
        :disabled="game.loading"
      />
      <button class="btn-send" @click="submitCustom" :disabled="game.loading || !customInput.trim()">
        发送
      </button>
    </div>

    <!-- NPC对话选项 -->
    <div v-if="game.inDialogue && !game.gameOver && game.choices.length > 0" class="choices npc-choices">
      <div class="npc-prompt">
        <span class="npc-icon">💬</span>
        <span>与 {{ game.state.npc?.npc?.name || 'NPC' }} 对话中...</span>
      </div>
      <button
        v-for="(choice, i) in game.choices"
        :key="i"
        class="btn-choice btn-npc"
        @click="game.doNPCAction(choice)"
        :disabled="game.loading"
      >
        {{ choice }}
      </button>
    </div>

    <!-- 游戏结束面板 -->
    <div v-if="game.gameOver" class="game-over-panel">
      <div v-if="game.victory" class="victory-screen">
        <div class="victory-icon">🏆</div>
        <h2>游戏胜利！</h2>
        <p>你成功击败了暗影龙，获得了远古宝藏，并逃离了被诅咒的小镇！</p>
        <p class="victory-sub">你的传说将在这片大陆上永远流传……</p>
      </div>
      <div v-else class="defeat-screen">
        <div class="defeat-icon">💀</div>
        <h2>游戏结束</h2>
        <p>你的冒险结束了……在黑暗中倒下。</p>
        <p class="defeat-sub">诅咒小镇将继续等待下一个冒险者。</p>
      </div>
      <div class="game-over-actions">
        <button class="btn-primary" @click="game.startGame" :disabled="game.loading">
          重新开始
        </button>
        <button class="btn-secondary" @click="backToMenu">
          返回主界面
        </button>
      </div>
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

function backToMenu() {
  game.sessionId = null
  game.resetState()
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

.npc-choices {
  flex-direction: column;
}

.npc-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6aafff;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.npc-icon {
  font-size: 1.1rem;
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

.btn-npc {
  color: #6aafff;
  border-color: #2a3a4a;
}

.btn-npc:hover:not(:disabled) {
  border-color: #6aafff;
  background: #15152a;
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

/* 游戏结束面板 */
.game-over-panel {
  text-align: center;
  padding: 30px 20px;
  background: #0f0f18;
  border: 1px solid #2a2a3a;
  border-radius: 12px;
  margin-top: 8px;
}

.victory-screen h2 {
  color: #c9a84c;
  font-size: 1.5rem;
  margin: 12px 0 8px;
}

.victory-screen p {
  color: #d4c8a8;
  font-size: 0.95rem;
}

.victory-sub {
  color: #8a8070 !important;
  font-size: 0.85rem !important;
  margin-top: 6px;
  font-style: italic;
}

.victory-icon {
  font-size: 3rem;
}

.defeat-screen h2 {
  color: #ff6a6a;
  font-size: 1.5rem;
  margin: 12px 0 8px;
}

.defeat-screen p {
  color: #d4c8a8;
  font-size: 0.95rem;
}

.defeat-sub {
  color: #8a8070 !important;
  font-size: 0.85rem !important;
  margin-top: 6px;
  font-style: italic;
}

.defeat-icon {
  font-size: 3rem;
}

.game-over-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

.btn-primary {
  background: linear-gradient(135deg, #c9a84c, #8a6d2b);
  color: #0a0a0f;
  border: none;
  padding: 12px 32px;
  font-size: 1rem;
  font-family: 'Noto Serif SC', serif;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(201, 168, 76, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: #8a8070;
  border: 1px solid #3a3a4a;
  padding: 12px 32px;
  font-size: 1rem;
  font-family: 'Noto Serif SC', serif;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  border-color: #8a8070;
  color: #d4c8a8;
}
</style>

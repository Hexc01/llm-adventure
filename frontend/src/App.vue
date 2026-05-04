<template>
  <div class="app">
    <header class="header">
      <h1>暗黑传说</h1>
      <p class="subtitle">LLM 驱动的文字冒险</p>
    </header>

    <div v-if="!game.sessionId" class="start-screen">
      <div class="start-content">
        <p>一段未知的旅程等待着你……</p>
        <p class="start-hint">在被诅咒的小镇中，寻找隐藏的远古宝藏，击败守护龙，逃离诅咒！</p>
        <button class="btn-primary" @click="game.startGame" :disabled="game.loading">
          {{ game.loading ? '正在连接...' : '开始冒险' }}
        </button>
      </div>
    </div>

    <div v-else class="game-container">
      <StatusBar />
      <QuestTracker />
      <CombatPanel />
      <div class="main-area">
        <ChatWindow />
        <ChoicePanel />
      </div>
      <Inventory />
    </div>
  </div>
</template>

<script setup>
import { useGameStore } from './stores/game'
import ChatWindow from './components/ChatWindow.vue'
import ChoicePanel from './components/ChoicePanel.vue'
import StatusBar from './components/StatusBar.vue'
import CombatPanel from './components/CombatPanel.vue'
import QuestTracker from './components/QuestTracker.vue'
import Inventory from './components/Inventory.vue'

const game = useGameStore()
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0a0a0f;
  color: #d4c8a8;
  font-family: 'Noto Serif SC', serif;
  min-height: 100vh;
}

.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #2a2a3a;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 2rem;
  color: #c9a84c;
  text-shadow: 0 0 20px rgba(201, 168, 76, 0.3);
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-top: 5px;
}

.start-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.start-content {
  text-align: center;
}

.start-content p {
  font-size: 1.2rem;
  margin-bottom: 12px;
  color: #8a8070;
}

.start-hint {
  font-size: 0.9rem !important;
  color: #666 !important;
  margin-bottom: 30px !important;
  max-width: 400px;
  line-height: 1.6;
}

.btn-primary {
  background: linear-gradient(135deg, #c9a84c, #8a6d2b);
  color: #0a0a0f;
  border: none;
  padding: 14px 40px;
  font-size: 1.1rem;
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

.game-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>

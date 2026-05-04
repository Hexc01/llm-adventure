<template>
  <div class="chat-window" ref="chatRef">
    <div v-for="(msg, i) in game.messages" :key="i" :class="['message', msg.role]">
      <div class="msg-content">
        <span v-if="msg.role === 'player'" class="label">你</span>
        <span v-else-if="msg.role === 'narrator'" class="label">旁白</span>
        <span v-else-if="msg.role === 'combat'" class="label combat-label">战斗</span>
        <span v-else class="label">系统</span>
        <p style="white-space: pre-line;">{{ msg.text }}</p>
      </div>
    </div>
    <div v-if="game.loading" class="message system">
      <div class="msg-content">
        <span class="label">旁白</span>
        <p class="typing">思考中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useGameStore } from '../stores/game'

const game = useGameStore()
const chatRef = ref(null)

watch(() => game.messages.length, async () => {
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
})
</script>

<style scoped>
.chat-window {
  flex: 1;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  background: #111118;
  border: 1px solid #2a2a3a;
  border-radius: 8px;
  padding: 16px;
}

.message {
  margin-bottom: 16px;
}

.msg-content {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.label {
  font-size: 0.8rem;
  color: #c9a84c;
  min-width: 32px;
  padding-top: 2px;
}

.message.player .label {
  color: #6a9eff;
}

.message.system .label {
  color: #ff6a6a;
}

.message.combat .label {
  color: #ff9a6a;
}

.message.combat p {
  color: #ffb38a;
}

.combat-label {
  color: #ff6a6a !important;
}

.message p {
  line-height: 1.8;
  font-size: 0.95rem;
}

.message.player p {
  color: #8ab4ff;
}

.typing::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

.chat-window::-webkit-scrollbar {
  width: 6px;
}

.chat-window::-webkit-scrollbar-track {
  background: #111118;
}

.chat-window::-webkit-scrollbar-thumb {
  background: #2a2a3a;
  border-radius: 3px;
}
</style>

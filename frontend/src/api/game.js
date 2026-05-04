import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export async function newGame() {
  const { data } = await api.post('/game/new')
  return data
}

export async function sendAction(sessionId, action) {
  const { data } = await api.post(`/game/action?session_id=${sessionId}`, { action })
  return data
}

export async function sendCombatAction(sessionId, tactic) {
  const { data } = await api.post(`/game/combat?session_id=${sessionId}`, { tactic })
  return data
}

export async function sendNPCAction(sessionId, action) {
  const { data } = await api.post(`/game/npc?session_id=${sessionId}`, { action })
  return data
}

<template>
  <div class="chat-page">
    <div class="chat-header flex justify-between items-center">
      <h2>AI问答 · 云小迹</h2>
      <button class="btn btn-ghost btn-sm" @click="clearHistory">清空对话</button>
    </div>

    <div class="chat-messages" ref="msgContainer">
      <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
        <div class="msg-avatar">{{ msg.role === 'user' ? '我' : '迹' }}</div>
        <div class="msg-bubble">
          <div class="msg-text" v-html="formatMsg(msg.content)"></div>
        </div>
      </div>
      <div v-if="thinking" class="msg-row assistant">
        <div class="msg-avatar">迹</div>
        <div class="msg-bubble typing">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>

    <div class="chat-input-bar">
      <textarea class="chat-input" v-model="inputText" placeholder="和云小迹聊聊吧..." @keydown.enter.exact.prevent="sendMsg" rows="1" :maxlength="1000"></textarea>
      <button class="btn btn-primary send-btn" :disabled="!inputText.trim() || thinking" @click="sendMsg">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { AI_CONFIG } from '../utils/config.js'

const messages = ref([
  { role: 'assistant', content: '你好！我是云小迹，云迹平台的AI助手。有什么可以帮你的吗？' }
])
const inputText = ref('')
const thinking = ref(false)
const msgContainer = ref(null)
let lastResponseId = null

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

function formatMsg(text) {
  return (text || '').replace(/\n/g, '<br>')
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  thinking.value = true
  scrollToBottom()

  try {
    const body = { model: AI_CONFIG.MODEL, input: text }
    if (lastResponseId) body.previous_response_id = lastResponseId
    else body.instructions = AI_CONFIG.SYSTEM_PROMPT

    const res = await fetch(AI_CONFIG.API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${AI_CONFIG.API_KEY}` },
      body: JSON.stringify(body)
    })
    const data = await res.json()

    if (data.id) lastResponseId = data.id
    const reply = extractReply(data)
    messages.value.push({ role: 'assistant', content: reply || '抱歉，我暂时无法回答这个问题。' })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '网络错误，请稍后重试。' })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

function extractReply(data) {
  if (data.output) {
    for (const item of data.output) {
      if (item.type === 'message' && item.content) {
        for (const c of item.content) {
          if (c.type === 'output_text') return c.text
        }
      }
    }
  }
  if (data.choices && data.choices[0]) return data.choices[0].message?.content
  return data.error?.message || ''
}

function clearHistory() {
  messages.value = [{ role: 'assistant', content: '对话已清空，有什么新问题吗？' }]
  lastResponseId = null
}

onMounted(() => scrollToBottom())
</script>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: 100vh; max-width: 800px; margin: 0 auto; }
.chat-header { padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
.chat-header h2 { font-size: 1.1rem; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
.msg-row { display: flex; gap: 10px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 600; flex-shrink: 0; }
.msg-row.assistant .msg-avatar { background: var(--primary); color: #fff; }
.msg-row.user .msg-avatar { background: var(--success); color: #fff; }
.msg-bubble { max-width: 70%; padding: 10px 14px; border-radius: 16px; font-size: 0.9rem; line-height: 1.6; word-break: break-word; }
.msg-row.assistant .msg-bubble { background: #F0F2F5; border-bottom-left-radius: 4px; }
.msg-row.user .msg-bubble { background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.typing { display: flex; gap: 6px; align-items: center; padding: 14px 18px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-muted); animation: dotBounce 1.4s infinite ease-in-out both; }
.dot:nth-child(2) { animation-delay: 0.16s; }
.dot:nth-child(3) { animation-delay: 0.32s; }
@keyframes dotBounce { 0%,80%,100% { transform: scale(0.6); } 40% { transform: scale(1); } }
.chat-input-bar { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
.chat-input { flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius-sm); font-size: 0.9rem; resize: none; outline: none; }
.chat-input:focus { border-color: var(--primary); }
.send-btn { flex-shrink: 0; }

@media (min-width: 768px) {
  .chat-page { height: calc(100vh - 0px); }
  .msg-bubble { max-width: 60%; }
}
</style>

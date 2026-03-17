<template>
  <div class="chat-detail-page">
    <div class="chat-header flex items-center gap-12">
      <button class="btn btn-ghost btn-sm" @click="$router.back()">← 返回</button>
      <h3>{{ peerName }}</h3>
    </div>

    <div class="messages-area" ref="msgArea">
      <div v-for="msg in messages" :key="msg._id" class="msg-row" :class="msg.fromId === myId ? 'self' : 'peer'">
        <div class="msg-avatar">{{ msg.fromId === myId ? '我' : (peerName || '?')[0] }}</div>
        <div class="msg-bubble">{{ msg.content }}</div>
      </div>
      <div v-if="!messages.length" class="empty-state">
        <div class="text text-sm">开始你们的对话吧</div>
      </div>
    </div>

    <div class="input-bar">
      <input class="chat-input form-input" v-model="inputText" placeholder="发送消息..." @keyup.enter="send" />
      <button class="btn btn-primary" :disabled="!inputText.trim()" @click="send">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'

const route = useRoute()
const { state } = useUserStore()
const peerId = route.params.peerId
const peerName = ref(decodeURIComponent(route.query.name || '用户'))
const myId = state.userInfo?._id
const messages = ref([])
const inputText = ref('')
const msgArea = ref(null)

function scrollBottom() {
  nextTick(() => { if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight })
}

async function loadMessages() {
  try {
    const result = await api.getChatHistory(peerId)
    messages.value = result.messages || []
    scrollBottom()
  } catch { /* ignore */ }
}

async function send() {
  if (!inputText.value.trim()) return
  try {
    await api.sendMessage(peerId, inputText.value.trim())
    inputText.value = ''
    await loadMessages()
  } catch { /* ignore */ }
}

onMounted(() => loadMessages())
</script>

<style scoped>
.chat-detail-page { display: flex; flex-direction: column; height: 100vh; max-width: 700px; margin: 0 auto; }
.chat-header { padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
.messages-area { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.msg-row { display: flex; gap: 8px; }
.msg-row.self { flex-direction: row-reverse; }
.msg-avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0; }
.msg-row.peer .msg-avatar { background: var(--primary); color: #fff; }
.msg-row.self .msg-avatar { background: var(--success); color: #fff; }
.msg-bubble { max-width: 65%; padding: 10px 14px; border-radius: 16px; font-size: 0.9rem; line-height: 1.5; word-break: break-word; }
.msg-row.peer .msg-bubble { background: #F0F2F5; border-bottom-left-radius: 4px; }
.msg-row.self .msg-bubble { background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.input-bar { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
.chat-input { flex: 1; }
</style>

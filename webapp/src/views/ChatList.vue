<template>
  <div class="page-container">
    <div class="page-header">
      <h2>私信</h2>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="conversations.length">
      <div v-for="conv in conversations" :key="conv.peerId" class="conv-item card mb-8" @click="goChat(conv)">
        <div class="flex items-center gap-12">
          <div class="avatar">{{ (conv.peerName || '?')[0] }}</div>
          <div class="conv-info">
            <div class="flex justify-between items-center">
              <span class="font-bold">{{ conv.peerName }}</span>
              <span class="text-xs text-muted">{{ formatTime(conv.lastTime) }}</span>
            </div>
            <p class="text-sm text-secondary conv-last">{{ conv.lastContent }}</p>
          </div>
          <span v-if="conv.unreadCount" class="unread-badge">{{ conv.unreadCount }}</span>
        </div>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">💌</div>
      <div class="text">暂无私信，在广场点击头像即可发起对话</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')
const conversations = ref([])
const loading = ref(false)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function loadData() {
  loading.value = true
  try {
    const result = await api.getConversations()
    conversations.value = result.conversations || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function goChat(conv) {
  router.push(`/chat/${conv.peerId}?name=${encodeURIComponent(conv.peerName)}`)
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.conv-item { cursor: pointer; transition: var(--transition); }
.conv-item:hover { box-shadow: var(--shadow-lg); }
.conv-info { flex: 1; min-width: 0; }
.conv-last { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.unread-badge { background: var(--danger); color: #fff; font-size: 0.7rem; padding: 2px 7px; border-radius: 100px; font-weight: 600; }
</style>

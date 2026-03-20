<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>处理历史记录</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.push('/settings')">返回</button>
    </div>
    <p class="text-sm text-muted mb-16">以下为你在当前负责班级内审核过的帖子、文件与闪光时刻（成果）。</p>

    <div class="tabs mb-16">
      <button class="tab-btn" :class="{ active: tab === 'posts' }" @click="tab = 'posts'">帖子</button>
      <button class="tab-btn" :class="{ active: tab === 'files' }" @click="tab = 'files'">文件</button>
      <button class="tab-btn" :class="{ active: tab === 'achievements' }" @click="tab = 'achievements'">闪光时刻</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else>
      <div v-if="filteredLogs.length" class="log-list">
        <div v-for="l in filteredLogs" :key="l._id" class="card mb-8 log-card">
          <div class="flex justify-between items-start mb-4">
            <span class="badge" :class="badgeClass(l)">{{ actionLabel(l) }}</span>
            <span class="text-xs text-muted">{{ l.createdAt }}</span>
          </div>
          <p class="text-sm">{{ summaryText(l) }}</p>
          <p v-if="l.detail?.authorNickname" class="text-xs text-muted mt-8">
            提交者：{{ l.detail.authorNickname }}
          </p>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="icon">📋</div>
        <div class="text">暂无记录</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import * as api from '../../api/index.js'

const showToast = inject('showToast')
const tab = ref('posts')
const logs = ref([])
const loading = ref(false)

const filteredLogs = computed(() => {
  const map = { posts: 'post', files: 'file_share', achievements: 'achievement' }
  const t = map[tab.value]
  return logs.value.filter(l => l.targetType === t)
})

function badgeClass(l) {
  if (l.action?.includes('reject') || l.action === 'file_delete') return 'badge-danger'
  if (l.action?.includes('approve') || l.action === 'post_override') return 'badge-success'
  return 'badge-primary'
}

function actionLabel(l) {
  const a = l.action || ''
  if (a === 'post_override') {
    const st = l.detail?.newStatus || ''
    if (st === 'published') return '帖子 · 恢复发布'
    if (st === 'archived') return '帖子 · 封存'
    return '帖子 · 状态变更'
  }
  if (a === 'file_approve') return '文件 · 通过'
  if (a === 'file_delete') return '文件 · 删除'
  if (a === 'achievement_approve') return '闪光时刻 · 通过'
  if (a === 'achievement_reject') return '闪光时刻 · 驳回'
  return a
}

function summaryText(l) {
  const d = l.detail || {}
  if (l.targetType === 'post') return d.summary || '（无摘要）'
  if (l.targetType === 'file_share') return d.title || '文件分享'
  if (l.targetType === 'achievement') return d.title || '成果'
  return JSON.stringify(d).slice(0, 120)
}

async function load() {
  loading.value = true
  try {
    const r = await api.adminGetReviewHistory()
    logs.value = r.logs || []
  } catch (e) {
    showToast(e.message || '加载失败')
    logs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>

<style scoped>
.page-container { max-width: 720px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 8px; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn {
  padding: 8px 16px; border-radius: var(--radius-sm);
  font-size: 0.85rem; background: var(--bg); border: 1px solid var(--border);
  color: var(--text-secondary);
}
.tab-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.log-card { border-left: 3px solid var(--primary); }
.badge-success { background: #E8F5E9; color: #2E7D32; }
.badge-danger { background: #FFEBEE; color: #C62828; }
</style>

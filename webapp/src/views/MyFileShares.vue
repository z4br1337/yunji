<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>我分享的文件</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="items.length">
      <div v-for="item in items" :key="item._id" class="card mb-8 file-card">
        <div class="flex items-start gap-12">
          <div class="flex-1 min-w-0">
            <h4 class="mb-4">{{ item.title }}</h4>
            <p v-if="item.description" class="text-sm text-secondary mb-8">{{ item.description }}</p>
            <div class="flex items-center gap-8 flex-wrap">
              <span class="badge" :class="item.status === 'approved' ? 'badge-success' : 'badge-warning'">
                {{ item.status === 'approved' ? '已通过' : '待审核' }}
              </span>
              <a v-if="item.status === 'approved'" :href="item.fileUrl" target="_blank" rel="noopener" class="btn btn-primary btn-sm">
                📎 下载 {{ item.fileName || '文件' }}
              </a>
              <span class="text-xs text-muted">{{ formatTime(item.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">📁</div>
      <div class="text">暂无分享文件</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import * as api from '../api/index.js'

const showToast = inject('showToast')
const items = ref([])
const loading = ref(false)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadItems() {
  loading.value = true
  try {
    const result = await api.getFileShareList({ myFiles: true, pageSize: 50 })
    items.value = result.items || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => loadItems())
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.file-card { transition: var(--transition); }
.flex-1 { flex: 1; }
.min-w-0 { min-width: 0; }
</style>

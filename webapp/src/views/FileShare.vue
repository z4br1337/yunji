<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>文件分享</h2>
      <button class="btn btn-primary btn-sm" @click="showCreate = true">分享文件</button>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal-card card">
        <h4 class="mb-16">分享学习文件</h4>
        <div class="form-group">
          <label class="form-label">标题 *</label>
          <input class="form-input" v-model="createForm.title" placeholder="例如：高等数学复习资料" />
        </div>
        <div class="form-group">
          <label class="form-label">描述（可选）</label>
          <textarea class="form-textarea" v-model="createForm.description" placeholder="简要描述文件内容" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">文件 *</label>
          <div class="file-upload-row">
            <label class="btn btn-ghost btn-sm">
              <input type="file" accept="*" hidden @change="onFileSelect" />
              {{ createForm.fileName || '选择文件' }}
            </label>
            <span v-if="createForm.fileError" class="text-danger text-xs">{{ createForm.fileError }}</span>
          </div>
        </div>
        <div class="flex gap-8 mt-16">
          <button class="btn btn-ghost" @click="showCreate = false">取消</button>
          <button class="btn btn-primary" :disabled="submitting" @click="submitFile">
            {{ submitting ? '上传中...' : '发布' }}
          </button>
        </div>
      </div>
    </div>

    <!-- List -->
    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="items.length">
      <div v-for="item in items" :key="item._id" class="card mb-8 file-card">
        <div class="flex items-start gap-12">
          <div class="avatar avatar-sm">
            <img v-if="item.authorAvatarUrl" :src="item.authorAvatarUrl" alt="" />
            <span v-else>{{ (item.authorName || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="mb-4">{{ item.title }}</h4>
            <p v-if="item.description" class="text-sm text-secondary mb-8">{{ item.description }}</p>
            <div class="flex items-center gap-8 flex-wrap">
              <a :href="item.fileUrl" target="_blank" rel="noopener" class="btn btn-primary btn-sm">
                📎 下载 {{ item.fileName || '文件' }}
              </a>
              <span class="text-xs text-muted">{{ item.authorName }} · {{ formatTime(item.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="hasMore" class="load-more">
        <button class="btn btn-ghost btn-sm" @click="loadMore">加载更多</button>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">📁</div>
      <div class="text">暂无分享文件，快来分享第一个吧！</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import * as api from '../api/index.js'

const showToast = inject('showToast')
const items = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const showCreate = ref(false)
const submitting = ref(false)
const createForm = ref({
  title: '',
  description: '',
  fileUrl: '',
  fileName: '',
  file: null,
  fileError: ''
})

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function onFileSelect(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  createForm.value.file = file
  createForm.value.fileName = file.name
  createForm.value.fileError = ''
}

async function submitFile() {
  const f = createForm.value
  if (!f.title.trim()) { showToast('请输入标题'); return }
  if (!f.file) { showToast('请选择文件'); return }
  submitting.value = true
  try {
    const uploadResult = await api.uploadFile(f.file)
    await api.createFileShare({
      title: f.title.trim(),
      description: f.description.trim(),
      fileUrl: uploadResult.url,
      fileName: uploadResult.fileName || f.fileName
    })
    showToast('分享成功')
    showCreate.value = false
    createForm.value = { title: '', description: '', fileUrl: '', fileName: '', file: null, fileError: '' }
    loadItems(true)
  } catch (e) {
    showToast(e.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

async function loadItems(reset = true) {
  if (reset) { page.value = 1; items.value = [] }
  loading.value = true
  try {
    const result = await api.getFileShareList({ page: page.value, pageSize: 20 })
    if (reset) {
      items.value = result.items || []
    } else {
      items.value = [...items.value, ...(result.items || [])]
    }
    hasMore.value = result.hasMore || false
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value++
  loadItems(false)
}

onMounted(() => loadItems())
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.file-card { transition: var(--transition); }
.file-card:hover { box-shadow: var(--shadow-lg); }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  padding: 16px;
}
.modal-card { max-width: 480px; width: 100%; }
.file-upload-row { display: flex; align-items: center; gap: 12px; }
.text-danger { color: var(--danger); }
.load-more { text-align: center; padding: 16px; }
.flex-1 { flex: 1; }
.min-w-0 { min-width: 0; }
</style>

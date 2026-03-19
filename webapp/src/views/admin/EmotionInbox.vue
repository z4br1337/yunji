<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>情感倾诉信息</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="posts.length">
      <div v-for="p in posts" :key="p._id" class="card mb-8 emotion-card clickable" @click="goToDetail(p._id)">
        <div class="flex justify-between items-center mb-4">
          <span class="font-bold">匿名倾诉</span>
          <span class="text-xs text-muted">{{ p.createdAt }}</span>
        </div>
        <p class="text-sm">{{ p.content }}</p>
        <div v-if="p.needOffline" class="offline-info mt-8">
          <span class="badge badge-warning">需要线下辅导</span>
          <span class="text-sm" v-if="p.offlineTime">时间: {{ p.offlineTime }}</span>
          <span class="text-sm" v-if="p.offlinePlace">地点: {{ p.offlinePlace }}</span>
        </div>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">📬</div>
      <div class="text">暂无情感倾诉信息</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../../api/index.js'

const router = useRouter()
const showToast = inject('showToast')
const posts = ref([])
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const result = await api.adminGetEmotionPosts()
    posts.value = result.posts || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function goToDetail(postId) {
  router.push(`/admin/emotion-inbox/${postId}`)
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.emotion-card { border-left: 3px solid #42A5F5; }
.emotion-card.clickable { cursor: pointer; transition: opacity 0.2s; }
.emotion-card.clickable:hover { opacity: 0.9; }
.offline-info { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; background: #FFF8E1; padding: 8px 12px; border-radius: var(--radius-sm); }
</style>

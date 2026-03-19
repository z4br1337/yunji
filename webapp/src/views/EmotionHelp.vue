<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>情感倾诉专线</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div class="tip-card card mb-16">
      <p class="text-sm">这里是你的私密倾诉空间。内容仅你和导生可见，默认匿名发布。</p>
    </div>

    <!-- Post Form -->
    <div class="card mb-16">
      <div class="form-group">
        <label class="form-label">说说你的心事</label>
        <textarea class="form-textarea" v-model="content" placeholder="写下你的想法..." rows="5" maxlength="2000"></textarea>
      </div>
      <div class="form-group">
        <label class="switch-row">
          <span>是否需要线下辅导</span>
          <input type="checkbox" v-model="needOffline" class="toggle" />
        </label>
      </div>
      <template v-if="needOffline">
        <div class="form-group">
          <label class="form-label">时间</label>
          <input class="form-input" v-model="offlineTime" placeholder="例如：周三下午2点" />
        </div>
        <div class="form-group">
          <label class="form-label">地点</label>
          <input class="form-input" v-model="offlinePlace" placeholder="例如：图书馆一楼" />
        </div>
      </template>
      <button class="btn btn-primary btn-block" :disabled="submitting" @click="submit">
        {{ submitting ? '发送中...' : '发送倾诉' }}
      </button>
    </div>

    <!-- My Emotion Posts -->
    <h3 class="mb-8">我的倾诉记录</h3>
    <div v-if="posts.length">
      <div v-for="p in posts" :key="p._id" class="card mb-8 emotion-post-card clickable" @click="goToDetail(p._id)">
        <p class="text-sm">{{ p.content }}</p>
        <div class="flex justify-between mt-8 text-xs text-muted">
          <span>{{ p.createdAt }}</span>
          <span v-if="p.needOffline">需要线下辅导: {{ p.offlineTime }} {{ p.offlinePlace }}</span>
        </div>
        <p class="text-xs text-primary mt-4">点击查看详情与导生回复 ›</p>
      </div>
    </div>
    <div v-else class="empty-state">
      <div class="icon">💙</div>
      <div class="text">暂无倾诉记录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')
const content = ref('')
const needOffline = ref(false)
const offlineTime = ref('')
const offlinePlace = ref('')
const submitting = ref(false)
const posts = ref([])

function goToDetail(postId) {
  router.push(`/emotion-help/${postId}`)
}

async function loadPosts() {
  try {
    const result = await api.getPosts({ category: 'emotion' })
    posts.value = (result.posts || []).filter(p => p.category === 'emotion')
  } catch { /* ignore */ }
}

async function submit() {
  if (!content.value.trim()) { showToast('请输入内容'); return }
  submitting.value = true
  try {
    await api.createPost({
      content: content.value, category: 'emotion', isAnonymous: true,
      needOffline: needOffline.value, offlineTime: offlineTime.value, offlinePlace: offlinePlace.value
    })
    showToast('发送成功')
    content.value = ''
    needOffline.value = false
    offlineTime.value = ''
    offlinePlace.value = ''
    await loadPosts()
  } catch (e) {
    showToast(e.message || '发送失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => loadPosts())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.tip-card { background: #E3F2FD; }
.tip-card p { color: #1565C0; }
.switch-row { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.toggle { width: 44px; height: 24px; appearance: none; background: #ccc; border-radius: 12px; position: relative; cursor: pointer; transition: var(--transition); }
.toggle:checked { background: var(--primary); }
.toggle::after { content: ''; position: absolute; width: 20px; height: 20px; background: #fff; border-radius: 50%; top: 2px; left: 2px; transition: var(--transition); }
.toggle:checked::after { left: 22px; }
.emotion-post-card.clickable { cursor: pointer; transition: opacity 0.2s; }
.emotion-post-card.clickable:hover { opacity: 0.9; }
.text-primary { color: var(--primary); }
</style>

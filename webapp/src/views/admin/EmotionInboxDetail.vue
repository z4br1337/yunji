<template>
  <div class="page-container emotion-detail">
    <div class="page-header flex justify-between items-center">
      <h2>情感倾诉详情</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="post">
      <!-- Post Header - 朋友圈风格，无通过/封存/置顶 -->
      <div class="emotion-post">
        <div class="post-header-row flex items-start gap-12">
          <div class="avatar avatar-square">{{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}</div>
          <div class="post-main flex-1">
            <span class="author-name">{{ post.visibleAuthorName || '匿名倾诉' }}</span>
            <div v-if="realAuthor" class="real-author-bar">真实身份：{{ realAuthor.nickname }}（{{ realAuthor.class }}）</div>
            <div class="post-content-area">
              <p class="post-content">{{ post.content }}</p>
              <div v-if="post.needOffline" class="offline-info">
                <span class="badge badge-warning">需要线下辅导</span>
                <span v-if="post.offlineTime">时间: {{ post.offlineTime }}</span>
                <span v-if="post.offlinePlace">地点: {{ post.offlinePlace }}</span>
              </div>
            </div>
            <div class="post-meta-row flex justify-between items-center">
              <span class="text-xs text-muted">{{ formatTime(post.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Comment Section - 浅灰背景块 -->
      <div class="comment-block">
        <div class="comment-arrow"></div>
        <div class="comment-list">
          <div v-for="c in comments" :key="c._id" class="comment-line">
            <span class="comment-author">{{ c.authorName }}:</span>
            <span class="comment-text">{{ c.content }}</span>
            <span class="comment-time">{{ formatTime(c.createdAt) }}</span>
          </div>
          <div v-if="!comments.length" class="comment-empty text-muted text-sm">暂无回复</div>
        </div>
        <div class="comment-input-area">
          <textarea class="form-textarea" v-model="newComment" placeholder="回复倾诉者..." rows="2" maxlength="500"></textarea>
          <button class="btn btn-primary btn-sm mt-8" :disabled="!newComment.trim()" @click="submitComment">发送</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { formatRelativeTime } from '../../utils/formatTime.js'
import * as api from '../../api/index.js'

const route = useRoute()
const showToast = inject('showToast')

const post = ref(null)
const realAuthor = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

function formatTime(ts) {
  return formatRelativeTime(ts)
}

async function loadData() {
  loading.value = true
  try {
    const result = await api.getPostDetail(route.params.postId)
    const p = Array.isArray(result.posts) ? result.posts[0] : result.post || result
    if (p && p.category !== 'emotion') {
      showToast('该内容不是情感倾诉')
      return
    }
    post.value = p || null
    if (p && p.authorName) {
      realAuthor.value = { nickname: p.authorName, class: p.authorClass || '' }
    }
    const cmtResult = await api.getComments(route.params.postId)
    comments.value = cmtResult.comments || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function submitComment() {
  if (!newComment.value.trim()) return
  try {
    await api.addComment(route.params.postId, newComment.value.trim())
    newComment.value = ''
    showToast('回复成功')
    const cmtResult = await api.getComments(route.params.postId)
    comments.value = cmtResult.comments || []
  } catch (e) {
    showToast(e.message || '回复失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.flex-1 { flex: 1; min-width: 0; }
.page-header { margin-bottom: 16px; }
.emotion-post { margin-bottom: 16px; }
.avatar-square { border-radius: 6px; min-width: 44px; width: 44px; height: 44px; }
.author-name { font-weight: 600; color: #576b95; font-size: 0.95rem; }
.real-author-bar { background: #FFF3CD; border-radius: var(--radius-sm); padding: 6px 10px; font-size: 0.8rem; color: #856404; margin-top: 6px; }
.post-content-area { margin-top: 8px; }
.post-content { font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.offline-info { margin-top: 8px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.8rem; color: var(--text-secondary); }
.post-meta-row { margin-top: 8px; }

.comment-block { background: #f7f7f7; border-radius: 8px; padding: 12px 16px; position: relative; }
.comment-arrow {
  position: absolute; top: -6px; left: 20px;
  width: 0; height: 0;
  border-left: 6px solid transparent; border-right: 6px solid transparent;
  border-bottom: 6px solid #f7f7f7;
}
.comment-list { min-height: 24px; }
.comment-line { padding: 6px 0; font-size: 0.9rem; line-height: 1.5; display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px; }
.comment-author { color: #576b95; font-weight: 500; }
.comment-text { color: #333; flex: 1; min-width: 0; }
.comment-time { font-size: 0.75rem; color: var(--text-muted); flex-shrink: 0; }
.comment-empty { padding: 12px 0; }
.comment-input-area { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e5e5; }
</style>

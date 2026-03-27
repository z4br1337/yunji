<template>
  <div class="page-container emotion-detail">
    <div class="page-header flex justify-between items-center">
      <h2>情感倾诉详情</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="post">
      <!-- Post Header - 朋友圈风格 -->
      <div class="emotion-post">
        <div class="post-header-row flex items-start gap-12">
          <div class="avatar avatar-square">{{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}</div>
          <div class="post-main flex-1">
            <span class="author-name">{{ post.visibleAuthorName || '匿名倾诉' }}</span>
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
            <div v-if="canDeleteEmotion" class="emotion-actions mt-12">
              <button type="button" class="btn btn-danger btn-sm" @click="onDeleteEmotion">删除倾诉</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Comment Section - 浅灰背景块 -->
      <div class="comment-block">
        <div class="comment-arrow"></div>
        <div class="comment-list">
          <div v-for="c in comments" :key="c._id" class="comment-line">
            <div class="comment-line-main">
              <span class="comment-author">{{ c.authorName }}:</span>
              <span v-if="c.parentCommentId && c.parentAuthorName" class="comment-reply-tag">@{{ c.parentAuthorName }}</span>
              <span class="comment-text">{{ c.content }}</span>
              <span class="comment-time">{{ formatTime(c.createdAt) }}</span>
            </div>
            <button type="button" class="btn-reply-emotion" @click="startReply(c)">回复</button>
          </div>
          <div v-if="!comments.length" class="comment-empty text-muted text-sm">暂无回复</div>
        </div>
        <div class="comment-input-area">
          <p v-if="replyingTo" class="replying-hint text-sm">
            回复 <strong>@{{ replyingTo.authorName }}</strong>
            <button type="button" class="btn-cancel-mini" @click="cancelReply">取消</button>
          </p>
          <textarea
            class="form-textarea"
            v-model="newComment"
            :placeholder="replyingTo ? `回复 @${replyingTo.authorName}…` : '回复导生...'"
            rows="2"
            maxlength="500"
          ></textarea>
          <button class="btn btn-primary btn-sm mt-8" :disabled="!newComment.trim()" @click="submitComment">发送</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { SCHOOL_CLASSES } from '../utils/config.js'
import { formatRelativeTime } from '../utils/formatTime.js'
import { check as sensitiveCheck } from '../utils/sensitive.js'
import * as api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const showToast = inject('showToast')
const { state } = useUserStore()

const post = ref(null)
const canDeleteEmotion = computed(() => {
  const p = post.value
  const me = state.userInfo?._id
  if (!p || !me) return false
  if (p.authorId === me) return true
  if (!state.isAdmin) return false
  const myCls = (state.userInfo.class || '').trim()
  const ac = (p.authorClass || '').trim()
  return SCHOOL_CLASSES.includes(myCls) && ac === myCls
})
const comments = ref([])
const newComment = ref('')
const replyingTo = ref(null)
const loading = ref(true)

function startReply(c) {
  replyingTo.value = { _id: c._id, authorName: c.authorName || '用户' }
}

function cancelReply() {
  replyingTo.value = null
}

function formatTime(ts) {
  return formatRelativeTime(ts)
}

async function loadData() {
  loading.value = true
  try {
    const result = await api.getPostDetail(route.params.id)
    const p = Array.isArray(result.posts) ? result.posts[0] : result.post || result
    if (p && p.category !== 'emotion') {
      showToast('该内容不是情感倾诉')
      return
    }
    post.value = p || null
    const cmtResult = await api.getComments(route.params.id)
    comments.value = cmtResult.comments || []
  } catch (e) {
    showToast(e.message || '加载失败')
    if (e.message && e.message.includes('无权')) {
      setTimeout(() => router.push('/emotion-help'), 1500)
    }
  } finally {
    loading.value = false
  }
}

async function onDeleteEmotion() {
  if (!post.value) return
  if (!window.confirm('确定删除该情感倾诉？删除后不可恢复。')) return
  try {
    await api.deletePost(post.value._id)
    showToast('已删除')
    router.replace('/emotion-help')
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

async function submitComment() {
  const text = newComment.value.trim()
  if (!text) return
  if (!sensitiveCheck(text).pass) {
    showToast('评论包含敏感词，无法发送')
    return
  }
  try {
    const opts = replyingTo.value ? { parentCommentId: replyingTo.value._id } : {}
    await api.addComment(route.params.id, text, opts)
    newComment.value = ''
    replyingTo.value = null
    showToast('回复成功')
    const cmtResult = await api.getComments(route.params.id)
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
.post-content-area { margin-top: 8px; }
.post-content { font-size: 0.9rem; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.offline-info { margin-top: 8px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 0.8rem; color: var(--text-secondary); }
.post-meta-row { margin-top: 8px; }
.emotion-actions { padding-top: 8px; border-top: 1px solid var(--border); }

.comment-block { background: #f7f7f7; border-radius: 8px; padding: 12px 16px; position: relative; }
.comment-arrow {
  position: absolute; top: -6px; left: 20px;
  width: 0; height: 0;
  border-left: 6px solid transparent; border-right: 6px solid transparent;
  border-bottom: 6px solid #f7f7f7;
}
.comment-list { min-height: 24px; }
.comment-line {
  padding: 8px 0;
  font-size: 0.9rem;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  border-bottom: 1px solid #ececec;
}
.comment-line:last-of-type { border-bottom: none; }
.comment-line-main { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px; flex: 1; min-width: 0; }
.comment-author { color: #576b95; font-weight: 500; }
.comment-reply-tag { font-size: 0.75rem; color: var(--primary); }
.comment-text { color: #333; flex: 1; min-width: 0; }
.comment-time { font-size: 0.75rem; color: var(--text-muted); flex-shrink: 0; width: 100%; }
.btn-reply-emotion {
  border: none;
  background: none;
  color: var(--primary);
  font-size: 0.75rem;
  cursor: pointer;
  flex-shrink: 0;
  padding: 2px 0;
}
.replying-hint { margin-bottom: 8px; color: #666; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.btn-cancel-mini {
  border: none;
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  cursor: pointer;
}
.comment-empty { padding: 12px 0; }
.comment-input-area { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e5e5; }
</style>

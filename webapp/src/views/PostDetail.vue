<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>帖子详情</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="post">
      <!-- Post Content -->
      <div class="card mb-16">
        <div class="detail-header flex items-center gap-12 mb-8">
          <div class="avatar" :class="{ clickable: !post.isAnonymous }" @click="onAuthorClick">
            {{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}
          </div>
          <div>
            <div class="flex items-center gap-8">
              <span class="font-bold">{{ post.visibleAuthorName || '匿名用户' }}</span>
              <span v-if="post.pinned" class="pin-badge">📌 置顶</span>
            </div>
            <span class="text-xs text-muted">{{ post.createdAt }}</span>
          </div>
        </div>

        <!-- Admin: show real author -->
        <div v-if="isAdmin && realAuthor" class="real-author-bar">
          真实身份：{{ realAuthor.nickname }}（{{ realAuthor.class }}）
        </div>

        <p class="detail-content">{{ post.content }}</p>

        <div v-if="post.images && post.images.length" class="detail-images">
          <img v-for="(img, i) in post.images" :key="i" :src="img" class="detail-img" loading="lazy" />
        </div>

        <!-- Admin actions (情感倾诉使用独立详情页，不显示) -->
        <div v-if="isAdmin && post.category !== 'emotion'" class="admin-actions mt-16">
          <button class="btn btn-sm btn-danger" @click="onDeletePost">删除</button>
          <button class="btn btn-sm btn-success" @click="onAction('published')">通过</button>
          <button class="btn btn-sm btn-warning" @click="onAction('archived')">封存</button>
          <button v-if="!post.pinned" class="btn btn-sm btn-ghost" @click="onPin">置顶</button>
          <button v-else class="btn btn-sm btn-ghost" @click="onUnpin">取消置顶</button>
        </div>

        <div v-else-if="isOwner && post.category !== 'emotion'" class="owner-actions mt-16">
          <button class="btn btn-sm btn-danger" @click="onDeletePost">删除帖子</button>
        </div>
      </div>

      <!-- Comments -->
      <div class="card">
        <h3 class="mb-8">评论 ({{ comments.length }})</h3>
        <div
          v-for="c in comments"
          :key="c._id"
          class="comment-item"
          :class="{
            'comment-item-active': isAdmin && focusedCommentId === c._id,
            'comment-item-clickable': isAdmin,
          }"
          :tabindex="isAdmin ? 0 : undefined"
          @click="onCommentRowClick(c)"
          @keyup.enter="isAdmin && onCommentRowClick(c)"
        >
          <div class="flex items-center gap-8 mb-4">
            <div class="avatar avatar-sm">{{ (c.authorName || '?')[0] }}</div>
            <span class="font-bold text-sm">{{ c.authorName }}</span>
            <span v-if="c.isAdmin" class="badge badge-danger">导生</span>
            <span class="text-xs text-muted" style="margin-left:auto">{{ c.createdAt }}</span>
          </div>
          <p v-if="c.parentCommentId && c.parentAuthorName" class="text-xs text-muted reply-hint">
            回复 <span class="reply-at">@{{ c.parentAuthorName }}</span>
          </p>
          <p class="text-sm comment-body">{{ c.content }}</p>
          <div class="comment-row-actions" @click.stop>
            <button type="button" class="btn-reply" @click="startReply(c)">回复</button>
          </div>
          <div v-if="isAdmin && focusedCommentId === c._id" class="comment-admin-actions" @click.stop>
            <button type="button" class="btn btn-danger btn-sm" @click="removeComment(c)">删除评论</button>
          </div>
        </div>

        <div v-if="!comments.length" class="text-muted text-sm text-center p-16">暂无评论</div>

        <!-- Add comment -->
        <div class="comment-input mt-16">
          <p v-if="replyingTo" class="replying-bar text-sm">
            正在回复 <strong>@{{ replyingTo.authorName }}</strong>
            <button type="button" class="btn-cancel-reply" @click="cancelReply">取消</button>
          </p>
          <textarea
            class="form-textarea"
            v-model="newComment"
            :placeholder="replyingTo ? `回复 @${replyingTo.authorName}…` : '写一条评论...'"
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
import { check as sensitiveCheck } from '../utils/sensitive.js'
import * as api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const { state } = useUserStore()
const showToast = inject('showToast')
const refreshInteractionUnread = inject('refreshInteractionUnread', () => {})

const isAdmin = computed(() => state.isAdmin)
const focusedCommentId = ref(null)
const isOwner = computed(() => {
  const p = post.value
  const me = state.userInfo?._id
  return !!(p && me && p.authorId === me)
})
const post = ref(null)
const realAuthor = ref(null)
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

async function loadData() {
  loading.value = true
  try {
    const result = await api.getPostDetail(route.params.id)
    const p = Array.isArray(result.posts) ? result.posts[0] : result.post || result
    post.value = p || null
    if (isAdmin.value && p && p.authorName) {
      realAuthor.value = { nickname: p.authorName, class: p.authorClass || '' }
    }
    const cmtResult = await api.getComments(route.params.id)
    comments.value = cmtResult.comments || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function onCommentRowClick(c) {
  if (!isAdmin.value) return
  focusedCommentId.value = focusedCommentId.value === c._id ? null : c._id
}

async function removeComment(c) {
  if (!window.confirm('确定删除该评论？其下的回复也会被删除。')) return
  try {
    await api.deleteComment(c._id)
    focusedCommentId.value = null
    showToast('已删除')
    const cmtResult = await api.getComments(route.params.id)
    comments.value = cmtResult.comments || []
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

async function submitComment() {
  const text = newComment.value.trim()
  if (!text) return
  const checkResult = sensitiveCheck(text)
  if (!checkResult.pass) {
    showToast('评论包含敏感词，无法发送')
    return
  }
  try {
    const opts = replyingTo.value ? { parentCommentId: replyingTo.value._id } : {}
    await api.addComment(route.params.id, text, opts)
    newComment.value = ''
    replyingTo.value = null
    showToast('评论成功')
    const cmtResult = await api.getComments(route.params.id)
    comments.value = cmtResult.comments || []
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  } catch (e) {
    showToast(e.message || '评论失败')
  }
}

async function onAction(action) {
  try {
    await api.adminOverridePost(post.value._id, action)
    post.value.status = action
    showToast('操作成功')
  } catch (e) {
    showToast(e.message || '操作失败')
  }
}

async function onPin() {
  await api.adminPinPost(post.value._id)
  post.value.pinned = true
  showToast('已置顶')
}

async function onUnpin() {
  await api.adminUnpinPost(post.value._id)
  post.value.pinned = false
  showToast('已取消置顶')
}

async function onDeletePost() {
  if (!post.value) return
  if (!window.confirm('确定删除该帖子？删除后不可恢复。')) return
  try {
    await api.deletePost(post.value._id)
    showToast('已删除')
    router.back()
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

function onAuthorClick() {
  if (post.value.isAnonymous) { showToast('该用户匿名发布'); return }
  const myId = state.userInfo?._id
  if (post.value.authorId === myId) return
  router.push(`/chat/${post.value.authorId}?name=${encodeURIComponent(post.value.visibleAuthorName || '用户')}`)
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 1.3rem; }
.detail-content { font-size: 0.95rem; line-height: 1.8; white-space: pre-wrap; word-break: break-word; margin: 12px 0; }
.detail-images { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.detail-img { max-width: 200px; max-height: 200px; border-radius: var(--radius-sm); object-fit: cover; }
.real-author-bar { background: #FFF3CD; border-radius: var(--radius-sm); padding: 8px 12px; font-size: 0.8rem; color: #856404; margin-bottom: 8px; }
.pin-badge { font-size: 0.7rem; background: #FFF3CD; color: #856404; padding: 1px 6px; border-radius: 4px; }
.admin-actions, .owner-actions { display: flex; gap: 8px; flex-wrap: wrap; padding-top: 12px; border-top: 1px solid var(--border); }
.comment-item { padding: 12px 0; border-bottom: 1px solid var(--border); }
.comment-item:last-child { border-bottom: none; }
.comment-item-clickable { cursor: pointer; border-radius: var(--radius-sm); }
.comment-item-clickable:hover { background: var(--bg); }
.comment-item-active { background: rgba(74, 144, 217, 0.08); }
.reply-hint { margin: 0 0 4px 40px; }
.reply-at { color: var(--primary); font-weight: 600; }
.comment-body { margin-left: 40px; }
.comment-row-actions { margin-left: 40px; margin-top: 6px; }
.btn-reply {
  border: none;
  background: none;
  padding: 0;
  font-size: 0.8rem;
  color: var(--primary);
  cursor: pointer;
  font-weight: 500;
}
.btn-reply:hover { text-decoration: underline; }
.comment-admin-actions { margin-left: 40px; margin-top: 8px; }
.replying-bar {
  margin-bottom: 8px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.btn-cancel-reply {
  border: none;
  background: var(--border);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  cursor: pointer;
}
.clickable { cursor: pointer; }
</style>

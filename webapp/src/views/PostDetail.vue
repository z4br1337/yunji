<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>帖子详情</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="post">
      <!-- Post Content -->
      <div
        class="card mb-16 post-detail-main-card"
        :class="{ 'post-detail-boutique': post.boutique, 'post-detail-highlight': !post.boutique && (post.pinned || post.featured) }"
      >
        <div v-if="post.pinned || post.featured || post.boutique" class="detail-corner-badges">
          <span v-if="post.pinned" class="detail-corner-badge" title="置顶帖：在广场列表优先展示">📌 置顶</span>
          <span v-if="post.featured" class="detail-corner-badge" title="优质帖：导生标记的优质内容">⭐ 优质</span>
          <span v-if="post.boutique" class="detail-corner-badge detail-corner-boutique" title="精品帖：点赞数超过30自动展示">💎 精品</span>
        </div>
        <div class="detail-header flex items-center gap-12 mb-8">
          <div class="avatar" :class="{ clickable: !post.isAnonymous }" @click="onAuthorClick">
            {{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}
          </div>
          <div>
            <div class="flex items-center gap-8">
              <span class="font-bold">{{ post.visibleAuthorName || '匿名用户' }}</span>
            </div>
            <span class="text-xs text-muted">{{ post.createdAt }}</span>
          </div>
        </div>

        <!-- 导生端：展示绑定学号与班级（非昵称） -->
        <div v-if="isAdmin && post.category !== 'emotion'" class="real-author-bar">
          真实身份：{{ (post.authorStudentId && String(post.authorStudentId).trim()) || '未绑定学号' }}（{{ post.authorClass || '—' }}）
        </div>

        <p class="detail-content">{{ post.content }}</p>

        <div v-if="post.images && post.images.length" class="detail-images">
          <img
            v-for="(img, i) in post.images"
            :key="i"
            :src="img"
            class="detail-img"
            loading="lazy"
            decoding="async"
            :fetchpriority="i === 0 ? 'high' : 'low'"
          />
        </div>

        <div class="detail-actions-row flex flex-wrap justify-between items-end gap-12 mt-16 pt-16">
          <div class="detail-actions-left flex gap-8 flex-wrap">
            <template v-if="isAdmin && post.category !== 'emotion'">
              <button type="button" class="btn btn-sm btn-danger" @click="onDeletePost">删除</button>
              <button
                type="button"
                class="btn btn-sm"
                :class="post.featured ? 'btn-ghost' : 'btn-success'"
                @click="onToggleFeatured"
              >{{ post.featured ? '取消精品' : '精品' }}</button>
              <button type="button" class="btn btn-sm btn-warning" @click="onAction('archived')">封存</button>
              <button v-if="!post.pinned" type="button" class="btn btn-sm btn-ghost" @click="onPin">置顶</button>
              <button v-else type="button" class="btn btn-sm btn-ghost" @click="onUnpin">取消置顶</button>
            </template>
            <template v-else-if="isOwner && post.category !== 'emotion'">
              <button type="button" class="btn btn-sm btn-danger" @click="onDeletePost">删除帖子</button>
            </template>
          </div>

          <button
            v-if="post.category !== 'emotion'"
            type="button"
            class="btn-like-detail"
            :disabled="likeDisabled"
            :title="likeTitle"
            @click.stop="onLike"
          >
            <span aria-hidden="true">{{ post.likedByMe ? '❤️' : '🤍' }}</span>
            <span class="like-detail-label">点赞</span>
            <span class="like-detail-num">{{ post.likeCount ?? 0 }}</span>
          </button>
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
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { check as sensitiveCheck } from '../utils/sensitive.js'
import * as api from '../api/index.js'
import * as localPostCache from '../utils/localPostCache.js'

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
const comments = ref([])
const newComment = ref('')
const replyingTo = ref(null)
const loading = ref(true)

function applyReadCache(postId) {
  const c = localPostCache.getCachedReadPost(postId)
  if (!c?.post) return false
  post.value = { ...c.post }
  comments.value = Array.isArray(c.comments) ? [...c.comments] : []
  return true
}

const likeDisabled = computed(() => {
  const p = post.value
  if (!p || p.category === 'emotion') return true
  if (p.likedByMe) return true
  if (p.status === 'published') return false
  return !!(isAdmin.value || isOwner.value)
})

const likeTitle = computed(() => {
  if (!post.value || post.value.category === 'emotion') return ''
  if (post.value.likedByMe) return '你已点赞过本帖'
  if (likeDisabled.value) return '当前状态不可点赞'
  return '点赞：每人每帖一次；热度高更易在广场展示；超过30赞自动为精品帖'
})

function startReply(c) {
  replyingTo.value = { _id: c._id, authorName: c.authorName || '用户' }
}

function cancelReply() {
  replyingTo.value = null
}

async function loadData() {
  const id = route.params.id
  focusedCommentId.value = null
  replyingTo.value = null
  const fromCache = applyReadCache(id)
  loading.value = !fromCache
  try {
    const [result, cmtResult] = await Promise.all([
      api.getPostDetail(id),
      api.getComments(id),
    ])
    const p = Array.isArray(result.posts) ? result.posts[0] : result.post || result
    post.value = p || null
    comments.value = cmtResult.comments || []
    if (post.value) {
      localPostCache.cacheReadPost(post.value, comments.value)
    }
  } catch (e) {
    if (!fromCache || !post.value) {
      showToast(e.message || '加载失败')
      post.value = null
      comments.value = []
    } else {
      showToast('暂时无法刷新，显示为已缓存内容')
    }
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
    if (post.value) localPostCache.cacheReadPost(post.value, comments.value)
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
    if (post.value) localPostCache.cacheReadPost(post.value, comments.value)
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
    localPostCache.cacheReadPost(post.value, comments.value)
    showToast('操作成功')
  } catch (e) {
    showToast(e.message || '操作失败')
  }
}

async function onToggleFeatured() {
  if (!post.value) return
  try {
    const want = !post.value.featured
    await api.adminPostFeatured(post.value._id, want)
    post.value.featured = want
    if (want && ['pending', 'review', 'flagged'].includes(post.value.status)) {
      post.value.status = 'published'
      if (post.value.flagged) {
        post.value.flagged = false
        post.value.flaggedWords = []
        post.value.flaggedCategories = []
        post.value.flaggedHighlighted = ''
      }
    }
    localPostCache.cacheReadPost(post.value, comments.value)
    showToast(want ? '已设为优质帖' : '已取消优质标记')
  } catch (e) {
    showToast(e.message || '操作失败')
  }
}

async function onLike() {
  const p = post.value
  if (!p || p.category === 'emotion' || likeDisabled.value) return
  try {
    const r = await api.postLike(p._id)
    p.likeCount = r.likeCount ?? p.likeCount
    p.likedByMe = true
    p.boutique = p.category !== 'emotion' && (p.likeCount || 0) > 30
    localPostCache.cacheReadPost(p, comments.value)
    showToast('点赞成功')
  } catch (e) {
    showToast(e.message || '点赞失败')
  }
}

async function onPin() {
  await api.adminPinPost(post.value._id)
  post.value.pinned = true
  localPostCache.cacheReadPost(post.value, comments.value)
  showToast('已置顶')
}

async function onUnpin() {
  await api.adminUnpinPost(post.value._id)
  post.value.pinned = false
  localPostCache.cacheReadPost(post.value, comments.value)
  showToast('已取消置顶')
}

async function onDeletePost() {
  if (!post.value) return
  if (!window.confirm('确定删除该帖子？删除后不可恢复。')) return
  try {
    const pid = post.value._id
    await api.deletePost(pid)
    localPostCache.invalidateReadPost(pid)
    localPostCache.removePostFromAllFeedSnapshots(pid)
    showToast('已删除')
    router.back()
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

function onAuthorClick() {
  if (post.value.isAnonymous) { showToast('该用户匿名发布'); return }
  router.push({
    name: 'PersonalHome',
    params: { userId: post.value.authorId },
  })
}

onMounted(() => loadData())
watch(() => route.params.id, () => loadData())
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 1.3rem; }
.detail-content { font-size: 0.95rem; line-height: 1.8; white-space: pre-wrap; word-break: break-word; margin: 12px 0; }
.detail-images { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.detail-img { max-width: 200px; max-height: 200px; border-radius: var(--radius-sm); object-fit: cover; }
.post-detail-main-card { position: relative; }
.detail-corner-badges {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}
.detail-corner-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: #FFF3CD;
  color: #856404;
  font-weight: 600;
}
.detail-corner-boutique {
  background: rgba(255, 255, 255, 0.95);
  color: #1e4d8c;
  border: 1px solid rgba(30, 77, 140, 0.35);
}
.post-detail-boutique {
  background: linear-gradient(165deg, #3d7dcc 0%, #5a9fe6 38%, #e8f2fc 72%, #ffffff 100%);
  border: 1px solid rgba(37, 99, 184, 0.25);
}
.post-detail-main-card.post-detail-boutique .real-author-bar {
  background: rgba(255, 255, 255, 0.85);
}
.real-author-bar { background: #FFF3CD; border-radius: var(--radius-sm); padding: 8px 12px; font-size: 0.8rem; color: #856404; margin-bottom: 8px; }
.detail-actions-row { border-top: 1px solid var(--border); align-items: flex-end; }
.detail-actions-left { flex: 1; min-width: 0; }
.like-detail-label { font-size: 0.8rem; font-weight: 600; }
.like-detail-num { font-weight: 700; }
.btn-like-detail {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  flex-shrink: 0;
}
.btn-like-detail:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
}
.btn-like-detail:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
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

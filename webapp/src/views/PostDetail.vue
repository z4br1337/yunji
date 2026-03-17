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
          <img v-for="(img, i) in post.images" :key="i" :src="img" class="detail-img" />
        </div>

        <!-- Admin actions -->
        <div v-if="isAdmin" class="admin-actions mt-16">
          <button class="btn btn-sm btn-success" @click="onAction('published')">通过</button>
          <button class="btn btn-sm btn-warning" @click="onAction('archived')">封存</button>
          <button v-if="!post.pinned" class="btn btn-sm btn-ghost" @click="onPin">置顶</button>
          <button v-else class="btn btn-sm btn-ghost" @click="onUnpin">取消置顶</button>
        </div>
      </div>

      <!-- Comments -->
      <div class="card">
        <h3 class="mb-8">评论 ({{ comments.length }})</h3>
        <div v-for="c in comments" :key="c._id" class="comment-item">
          <div class="flex items-center gap-8 mb-4">
            <div class="avatar avatar-sm">{{ (c.authorName || '?')[0] }}</div>
            <span class="font-bold text-sm">{{ c.authorName }}</span>
            <span v-if="c.isAdmin" class="badge badge-danger">管理员</span>
            <span class="text-xs text-muted" style="margin-left:auto">{{ c.createdAt }}</span>
          </div>
          <p class="text-sm" style="margin-left:40px">{{ c.content }}</p>
        </div>

        <div v-if="!comments.length" class="text-muted text-sm text-center p-16">暂无评论</div>

        <!-- Add comment -->
        <div class="comment-input mt-16">
          <textarea class="form-textarea" v-model="newComment" placeholder="写一条评论..." rows="2" maxlength="500"></textarea>
          <button class="btn btn-primary btn-sm mt-8" :disabled="!newComment.trim()" @click="submitComment">发送</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const { state } = useUserStore()
const showToast = inject('showToast')

const isAdmin = ref(state.isAdmin)
const post = ref(null)
const realAuthor = ref(null)
const comments = ref([])
const newComment = ref('')
const loading = ref(true)

async function loadData() {
  loading.value = true
  try {
    const result = await api.getPostDetail(route.params.id)
    post.value = result.post
    realAuthor.value = result.realAuthor
    const cmtResult = await api.getComments(route.params.id)
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
    await api.addComment(route.params.id, newComment.value.trim())
    newComment.value = ''
    showToast('评论成功')
    const cmtResult = await api.getComments(route.params.id)
    comments.value = cmtResult.comments || []
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
.admin-actions { display: flex; gap: 8px; flex-wrap: wrap; padding-top: 12px; border-top: 1px solid var(--border); }
.comment-item { padding: 12px 0; border-bottom: 1px solid var(--border); }
.comment-item:last-child { border-bottom: none; }
.clickable { cursor: pointer; }
</style>

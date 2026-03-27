<template>
  <div class="interaction-page">
    <header class="interaction-top">
      <h1 class="interaction-title">互动信息</h1>
      <div class="interaction-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'dm'"
          class="tab-pill"
          :class="{ active: tab === 'dm' }"
          @click="tab = 'dm'"
        >
          私信
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'reply'"
          class="tab-pill"
          :class="{ active: tab === 'reply' }"
          @click="tab = 'reply'"
        >
          回复我的
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="tab === 'post'"
          class="tab-pill"
          :class="{ active: tab === 'post' }"
          @click="tab = 'post'"
        >
          评论我的
        </button>
      </div>
    </header>

    <!-- Tab 1: 私信 -->
    <div v-show="tab === 'dm'" class="tab-panel">
      <div v-if="loadingDm" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="conversations.length">
        <div
          v-for="conv in conversations"
          :key="conv.peerId"
          class="list-card conv-row"
          @click="goChat(conv)"
        >
          <div class="row-avatar">{{ (conv.peerName || '?')[0] }}</div>
          <div class="row-body">
            <div class="row-title-line">
              <span class="row-name">{{ conv.peerName }}</span>
              <span class="row-time">{{ formatDmTime(conv.lastTime) }}</span>
            </div>
            <p class="row-sub">{{ conv.lastContent }}</p>
          </div>
          <span v-if="conv.unreadCount" class="unread-pill">{{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}</span>
          <span class="row-chevron">›</span>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">💌</div>
        <div class="text">暂无私信，在广场点击头像即可发起对话</div>
      </div>
    </div>

    <!-- Tab 2: 回复我的 -->
    <div v-show="tab === 'reply'" class="tab-panel">
      <div v-if="loadingReply" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="replies.length">
        <div
          v-for="item in replies"
          :key="item.commentId"
          class="list-card interact-row"
          @click="goPost(item.postId)"
        >
          <div class="row-avatar row-avatar-img" v-if="item.fromAvatarUrl">
            <img :src="item.fromAvatarUrl" alt="" />
          </div>
          <div v-else class="row-avatar">{{ (item.fromName || '?')[0] }}</div>
          <div class="row-body">
            <div class="row-title-line">
              <span class="row-name">{{ item.fromName }}</span>
              <span class="row-time">{{ formatRel(item.createdAt) }}</span>
            </div>
            <p class="row-action">回复了你的评论</p>
            <p v-if="item.parentContent" class="row-quote">原评论：{{ item.parentContent }}</p>
            <p class="row-sub">回复：{{ item.replyContent }}</p>
          </div>
          <div class="thumb-wrap" v-if="item.postSnippet">
            <span class="thumb-text">{{ item.postSnippet }}</span>
          </div>
          <span class="row-chevron">›</span>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">💬</div>
        <div class="text">暂时没有人回复你的评论</div>
      </div>
    </div>

    <!-- Tab 3: 评论我的 -->
    <div v-show="tab === 'post'" class="tab-panel">
      <div v-if="loadingPost" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="postComments.length">
        <div
          v-for="item in postComments"
          :key="item.commentId"
          class="list-card interact-row"
          @click="goPost(item.postId)"
        >
          <div class="row-avatar row-avatar-img" v-if="item.fromAvatarUrl">
            <img :src="item.fromAvatarUrl" alt="" />
          </div>
          <div v-else class="row-avatar">{{ (item.fromName || '?')[0] }}</div>
          <div class="row-body">
            <div class="row-title-line">
              <span class="row-name">{{ item.fromName }}</span>
              <span class="row-time">{{ formatRel(item.createdAt) }}</span>
            </div>
            <p class="row-action">
              {{ item.parentAuthorName ? `回复了 @${item.parentAuthorName}` : '评论了你的动态' }}
            </p>
            <p class="row-sub">{{ item.content }}</p>
          </div>
          <div class="thumb-wrap" v-if="item.postSnippet">
            <span class="thumb-text">{{ item.postSnippet }}</span>
          </div>
          <span class="row-chevron">›</span>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">📝</div>
        <div class="text">你的帖子下还没有新评论</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'
import { formatRelativeTime } from '../utils/formatTime.js'

const router = useRouter()
const showToast = inject('showToast')
const refreshInteractionUnread = inject('refreshInteractionUnread', () => {})

const tab = ref('dm')
const conversations = ref([])
const replies = ref([])
const postComments = ref([])
const loadingDm = ref(false)
const loadingReply = ref(false)
const loadingPost = ref(false)

function formatDmTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function formatRel(ts) {
  return formatRelativeTime(ts)
}

async function loadDm() {
  loadingDm.value = true
  try {
    const result = await api.getConversations()
    conversations.value = result.conversations || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loadingDm.value = false
  }
}

async function loadReplies() {
  loadingReply.value = true
  try {
    const result = await api.getRepliesToMe()
    replies.value = result.items || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loadingReply.value = false
  }
}

async function loadPostComments() {
  loadingPost.value = true
  try {
    const result = await api.getCommentsOnMyPosts()
    postComments.value = result.items || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loadingPost.value = false
  }
}

function goChat(conv) {
  router.push(`/chat/${conv.peerId}?name=${encodeURIComponent(conv.peerName)}`)
}

function goPost(postId) {
  router.push(`/post/${postId}`)
}

watch(tab, (t) => {
  if (t === 'dm' && !conversations.value.length && !loadingDm.value) loadDm()
  if (t === 'reply' && !replies.value.length && !loadingReply.value) loadReplies()
  if (t === 'post' && !postComments.value.length && !loadingPost.value) loadPostComments()
})

onMounted(async () => {
  try {
    await api.markInteractionSeen('all')
    await refreshInteractionUnread()
  } catch { /* ignore */ }
  await loadDm()
})
</script>

<style scoped>
.interaction-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 12px 16px 24px;
  background: #fff;
  min-height: 100%;
}

.interaction-top {
  position: sticky;
  top: 0;
  z-index: 2;
  background: #fff;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.interaction-title {
  font-size: 1.15rem;
  font-weight: 700;
  text-align: center;
  margin: 0 0 14px;
  color: #161823;
}

.interaction-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
}

.tab-pill {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 4px 10px;
  font-size: 0.88rem;
  color: #666;
  cursor: pointer;
  position: relative;
  font-weight: 500;
}

.tab-pill.active {
  color: #161823;
  font-weight: 700;
}

.tab-pill.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 28px;
  height: 3px;
  background: #161823;
  border-radius: 2px;
}

.tab-panel {
  min-height: 200px;
}

.list-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.list-card:last-child {
  border-bottom: none;
}

.conv-row:hover,
.interact-row:hover {
  opacity: 0.92;
}

.row-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8f4fc, #d0e8f7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--primary);
  flex-shrink: 0;
  font-size: 1rem;
}

.row-avatar-img {
  padding: 0;
  overflow: hidden;
  background: #eee;
}

.row-avatar-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-body {
  flex: 1;
  min-width: 0;
}

.row-title-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.row-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: #161823;
}

.row-time {
  font-size: 0.72rem;
  color: #999;
  flex-shrink: 0;
}

.row-action {
  font-size: 0.8rem;
  color: #666;
  margin: 4px 0 2px;
}

.row-quote {
  font-size: 0.78rem;
  color: #888;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-sub {
  font-size: 0.85rem;
  color: #333;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.unread-pill {
  background: #fe2c55;
  color: #fff;
  font-size: 0.65rem;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
  align-self: center;
}

.row-chevron {
  color: #ccc;
  font-size: 1.1rem;
  flex-shrink: 0;
  align-self: center;
}

.thumb-wrap {
  width: 52px;
  height: 52px;
  border-radius: 6px;
  background: #f2f2f2;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: center;
}

.thumb-text {
  font-size: 0.55rem;
  color: #888;
  padding: 4px;
  line-height: 1.25;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--text-muted);
}

.empty-state .icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.empty-state .text {
  font-size: 0.9rem;
}
</style>

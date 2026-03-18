<template>
  <div class="feed-page">
    <div class="feed-header">
      <h2 class="page-title">广场</h2>
    </div>

    <!-- Category Tabs -->
    <div class="category-bar">
      <button v-for="cat in categories" :key="cat.key"
        class="cat-btn" :class="{ active: currentCategory === cat.key }"
        @click="switchCategory(cat.key)">
        {{ cat.label }}
      </button>
    </div>

    <!-- Post List -->
    <div class="post-list">
      <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="posts.length">
        <PostCard v-for="post in posts" :key="post._id" :post="post" :is-admin="isAdmin"
          @click="goDetail(post._id)" @avatar-click="onAvatarClick" />
        <div v-if="hasMore" class="load-more">
          <button class="btn btn-ghost btn-sm" @click="loadMore">加载更多</button>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">📭</div>
        <div class="text">暂无帖子，快去发布第一条吧！</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated, watch, inject } from 'vue'
import { useRouter, onBeforeRouteUpdate } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { POST_CATEGORIES } from '../utils/config.js'
import * as api from '../api/index.js'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const { state } = useUserStore()
const showToast = inject('showToast')
const isMobile = inject('isMobile', ref(false))

const isAdmin = computed(() => state.isAdmin)
const pageSize = computed(() => (isMobile.value ? 12 : 20))
const categories = [{ key: 'all', label: '全部' }, ...POST_CATEGORIES]
const currentCategory = ref('all')
const posts = ref([])
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
let loaded = false

async function loadPosts(reset = true) {
  if (reset) { page.value = 1; posts.value = [] }
  loading.value = true
  try {
    const params = { page: page.value, pageSize: pageSize.value, excludeEmotion: true }
    if (currentCategory.value !== 'all') params.category = currentCategory.value
    const result = await api.getPosts(params)
    if (reset) {
      posts.value = result.posts || []
    } else {
      posts.value = [...posts.value, ...(result.posts || [])]
    }
    hasMore.value = result.hasMore || false
    loaded = true
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function switchCategory(key) {
  currentCategory.value = key
  loadPosts()
}

function loadMore() {
  page.value++
  loadPosts(false)
}

function goDetail(id) {
  router.push(`/post/${id}`)
}

function onAvatarClick(post) {
  if (post.isAnonymous) { showToast('该用户匿名发布'); return }
  const myId = state.userInfo?._id
  if (post.authorId === myId) return
  router.push(`/chat/${post.authorId}?name=${encodeURIComponent(post.visibleAuthorName || '用户')}`)
}

onMounted(() => {
  if (state.isLoggedIn) {
    loadPosts()
  }
})

watch(() => state.isLoggedIn, (val) => {
  if (val && !loaded) loadPosts()
})
</script>

<style scoped>
.feed-page { max-width: 680px; margin: 0 auto; padding: 16px; }
.feed-header { margin-bottom: 16px; }
.page-title { font-size: 1.4rem; }
.category-bar { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px; -webkit-overflow-scrolling: touch; }
.category-bar::-webkit-scrollbar { display: none; }
.cat-btn {
  flex-shrink: 0; padding: 6px 16px; border-radius: 100px;
  font-size: 0.85rem; background: var(--bg-card); border: 1px solid var(--border);
  color: var(--text-secondary); transition: var(--transition); white-space: nowrap;
}
.cat-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.cat-btn:hover:not(.active) { border-color: var(--primary); color: var(--primary); }
.post-list { margin-top: 8px; }
.load-more { text-align: center; padding: 16px; }

@media (min-width: 768px) {
  .feed-page { padding: 24px 32px; }
}
</style>

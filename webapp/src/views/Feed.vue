<template>
  <div class="feed-page">
    <div class="feed-header">
      <h2 class="page-title">广场</h2>
    </div>

    <button type="button" class="search-entry" @click="goSearch">
      <span class="search-entry-icon" aria-hidden="true">🔍</span>
      <span class="search-entry-text">{{ searchPlaceholder }}</span>
    </button>
    <p v-if="filterHint" class="filter-hint text-sm text-muted">{{ filterHint }}</p>

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
      <div v-if="refreshing" class="refresh-strip" aria-hidden="true" title="正在更新"></div>
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
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { POST_CATEGORIES } from '../utils/config.js'
import * as api from '../api/index.js'
import * as localPostCache from '../utils/localPostCache.js'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const { state } = useUserStore()
const showToast = inject('showToast')
const isMobile = inject('isMobile', ref(false))

const isAdmin = computed(() => state.isAdmin)
const pageSize = computed(() => (isMobile.value ? 12 : 20))
const categories = [{ key: 'all', label: '全部' }, ...POST_CATEGORIES]
const currentCategory = ref('all')
const searchKeyword = ref('')
const activeTopic = ref('')
const posts = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const hasMore = ref(false)
let loaded = false

const searchPlaceholder = computed(() => {
  if (activeTopic.value) return `话题：#${activeTopic.value}#`
  if (searchKeyword.value) return `搜索：${searchKeyword.value}`
  return '搜索帖子、话题…'
})

const filterHint = computed(() => {
  const parts = []
  if (activeTopic.value) parts.push(`话题「#${activeTopic.value}#」`)
  if (searchKeyword.value) parts.push(`关键词「${searchKeyword.value}」`)
  if (!parts.length) return ''
  return `当前筛选：${parts.join(' · ')} · 点搜索框可修改`
})

function syncQueryFromRoute() {
  const q = route.query.q
  const t = route.query.topic
  searchKeyword.value = typeof q === 'string' ? q.trim() : ''
  activeTopic.value = typeof t === 'string' ? t.trim() : ''
}

async function loadPosts(reset = true) {
  if (reset) {
    page.value = 1
    const snap = localPostCache.getFeedSnapshot(
      currentCategory.value,
      searchKeyword.value,
      activeTopic.value,
      pageSize.value
    )
    if (snap?.posts?.length) {
      posts.value = snap.posts
      hasMore.value = !!snap.hasMore
      loaded = true
      loading.value = false
      refreshing.value = true
    } else {
      posts.value = []
      loading.value = true
      refreshing.value = false
    }
  } else {
    loading.value = true
  }

  try {
    const params = { page: page.value, pageSize: pageSize.value, excludeEmotion: true }
    if (currentCategory.value !== 'all') params.category = currentCategory.value
    const kw = searchKeyword.value.trim()
    if (kw) params.keyword = kw
    const tf = activeTopic.value.trim()
    if (tf) params.topic = tf
    const result = await api.getPosts(params)
    if (reset) {
      posts.value = result.posts || []
    } else {
      posts.value = [...posts.value, ...(result.posts || [])]
    }
    hasMore.value = result.hasMore || false
    loaded = true
    if (reset) {
      localPostCache.saveFeedSnapshot(
        currentCategory.value,
        searchKeyword.value,
        activeTopic.value,
        pageSize.value,
        posts.value,
        hasMore.value
      )
    }
  } catch (e) {
    if (!reset || posts.value.length === 0) {
      showToast(e.message || '加载失败')
    } else {
      showToast('网络异常，暂显示本地缓存')
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function switchCategory(key) {
  currentCategory.value = key
  router.replace({ path: '/feed', query: { ...route.query } })
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
  router.push({
    name: 'PersonalHome',
    params: { userId: post.authorId },
  })
}

function goSearch() {
  router.push('/search')
}

onMounted(() => {
  syncQueryFromRoute()
  if (state.isLoggedIn) {
    loadPosts()
  }
})

watch(() => state.isLoggedIn, (val) => {
  if (val && !loaded) loadPosts()
})

watch(
  () => route.query,
  () => {
    syncQueryFromRoute()
    if (state.isLoggedIn) loadPosts()
  },
  { deep: true }
)
</script>

<style scoped>
.feed-page { max-width: 680px; margin: 0 auto; padding: 16px; }
.feed-header { margin-bottom: 12px; }
.page-title { font-size: 1.4rem; }
.search-entry {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 22px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  box-shadow: var(--shadow);
  cursor: pointer;
  text-align: left;
  font-size: 0.95rem;
  color: var(--text-muted);
  transition: var(--transition);
  margin-bottom: 8px;
}
.search-entry:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.search-entry-icon { font-size: 1.1rem; opacity: 0.85; }
.search-entry-text { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.filter-hint { margin-bottom: 12px; line-height: 1.4; }
.category-bar { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 12px; -webkit-overflow-scrolling: touch; }
.category-bar::-webkit-scrollbar { display: none; }
.cat-btn {
  flex-shrink: 0; padding: 6px 16px; border-radius: 100px;
  font-size: 0.85rem; background: var(--bg-card); border: 1px solid var(--border);
  color: var(--text-secondary); transition: var(--transition); white-space: nowrap;
}
.cat-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.cat-btn:hover:not(.active) { border-color: var(--primary); color: var(--primary); }
.post-list { margin-top: 8px; position: relative; }
.refresh-strip {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: feed-refresh-pulse 1s ease-in-out infinite;
  z-index: 1; pointer-events: none;
}
@keyframes feed-refresh-pulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}
.load-more { text-align: center; padding: 16px; }

@media (min-width: 768px) {
  .feed-page { padding: 24px 32px; }
}
</style>

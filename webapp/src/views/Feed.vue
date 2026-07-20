<template>
  <div class="feed-page">
    <div class="hero-card card">
      <div class="hero-top">
        <div>
          <h2 class="page-title">广场</h2>
          <p class="hero-subtitle">关注校园动态、话题与同学们的真实分享</p>
        </div>
        <button type="button" class="hero-action" @click="goSearch">搜索</button>
      </div>
      <button type="button" class="search-entry" @click="goSearch">
        <span class="search-entry-icon" aria-hidden="true">搜索</span>
        <span class="search-entry-text">{{ searchPlaceholder }}</span>
      </button>
      <p v-if="filterHint" class="filter-hint text-sm text-muted">{{ filterHint }}</p>
    </div>

    <div class="category-bar">
      <button v-for="cat in categories" :key="cat.key" class="cat-btn" :class="{ active: currentCategory === cat.key }" @click="switchCategory(cat.key)">
        {{ cat.label }}
      </button>
    </div>

    <div class="post-list">
      <div v-if="refreshing" class="refresh-strip" aria-hidden="true" title="正在更新"></div>
      <button v-if="activityBanner" type="button" class="activity-feed-entry" @click="goActivity">
        <span class="activity-feed-icon" aria-hidden="true">活动</span>
        <span class="activity-feed-text">
          <span class="activity-feed-label">近期活动</span>
          <span class="activity-feed-title">{{ activityBanner.title }}</span>
        </span>
        <span class="activity-feed-arrow" aria-hidden="true">›</span>
      </button>
      <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="posts.length">
        <PostCard v-for="post in posts" :key="post._id" :post="post" :is-admin="isAdmin" @click="goDetail(post._id)" @avatar-click="onAvatarClick" />
        <div v-if="hasMore" class="load-more"><button class="btn btn-ghost btn-sm" @click="loadMore">加载更多</button></div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">暂无内容</div>
        <div class="text">先发布第一条帖子吧</div>
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
const activityBanner = ref(null)
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

function queryString(val) {
  if (typeof val === 'string') return val.trim()
  if (Array.isArray(val) && val.length) return String(val[0] ?? '').trim()
  return ''
}

function syncQueryFromRoute() {
  searchKeyword.value = queryString(route.query.q)
  activeTopic.value = queryString(route.query.topic)
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

function goActivity() {
  router.push({ name: 'ActivityList' })
}

async function loadActivityBanner() {
  try {
    const r = await api.listPublicActivityCampaigns()
    const list = r.campaigns || []
    if (!list.length) {
      activityBanner.value = null
      return
    }
    const featured = list.find((c) => c.isActive && String(c.tag || '').trim()) || list[0]
    activityBanner.value = featured && String(featured.title || '').trim() ? featured : null
  } catch {
    activityBanner.value = null
  }
}

onMounted(() => {
  syncQueryFromRoute()
  loadActivityBanner()
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

watch(
  () => route.path,
  (p) => {
    if (p === '/feed') loadActivityBanner()
  }
)
</script>

<style scoped>
.feed-page { max-width: 720px; margin: 0 auto; padding: 16px; }
.hero-card { margin-bottom: 14px; }
.hero-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.page-title { font-size: 1.4rem; font-weight: 700; }
.hero-subtitle { font-size: 0.84rem; color: var(--text-muted); margin-top: 4px; }
.hero-action {
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  background: rgba(255,130,0,0.12);
  color: var(--primary);
  font-weight: 600;
}
.search-entry {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg-muted);
  cursor: pointer;
  text-align: left;
  font-size: 0.95rem;
  color: var(--text-muted);
  transition: var(--transition);
}
.search-entry:hover { border-color: var(--primary); background: #fff; }
.search-entry-icon { font-size: 0.8rem; padding-right: 4px; color: var(--text-muted); }
.search-entry-text { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.filter-hint { margin-top: 8px; line-height: 1.4; }
.category-bar { display: flex; gap: 8px; overflow-x: auto; padding: 4px 0 12px; -webkit-overflow-scrolling: touch; }
.category-bar::-webkit-scrollbar { display: none; }
.cat-btn {
  flex-shrink: 0; padding: 7px 14px; border-radius: 999px;
  font-size: 0.84rem; background: #fff; border: 1px solid var(--border);
  color: var(--text-secondary); transition: var(--transition); white-space: nowrap;
}
.cat-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.post-list { margin-top: 4px; position: relative; }
.activity-feed-entry {
  width: 100%; display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; margin-bottom: 12px; border-radius: var(--radius);
  border: 1px solid var(--border); background: #fff; cursor: pointer;
  text-align: left; font-family: inherit; transition: var(--transition);
}
.activity-feed-entry:hover { border-color: var(--primary); background: rgba(255,130,0,0.04); }
.activity-feed-icon { font-size: 0.78rem; color: var(--primary); font-weight: 700; flex-shrink: 0; }
.activity-feed-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.activity-feed-label { font-size: 0.72rem; color: var(--text-muted); }
.activity-feed-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.activity-feed-arrow { font-size: 1.2rem; color: var(--text-muted); flex-shrink: 0; }
.refresh-strip {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--primary); opacity: 0.8; animation: feed-refresh-pulse 1s ease-in-out infinite;
  z-index: 1; pointer-events: none;
}
@keyframes feed-refresh-pulse { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
.load-more { text-align: center; padding: 16px; }
@media (min-width: 768px) { .feed-page { padding: 24px 32px; } }
</style>

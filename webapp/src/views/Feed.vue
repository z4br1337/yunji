<template>
  <div class="feed-page">
    <section class="feed-hero">
      <div class="feed-hero-top">
        <div>
          <p class="feed-kicker">云迹广场</p>
          <h2 class="page-title">发现校园里正在发生的事</h2>
          <p class="hero-subtitle">关注校园动态、话题、活动与同学们的真实分享</p>
        </div>
        <button type="button" class="hero-action" @click="goSearch">搜索</button>
      </div>

      <button type="button" class="search-entry" @click="goSearch" aria-label="搜索帖子、话题和活动">
        <span class="search-entry-icon" aria-hidden="true">⌕</span>
        <span class="search-entry-text">{{ searchPlaceholder }}</span>
        <span class="search-entry-hint">Search</span>
      </button>

      <div class="feed-stats">
        <div class="feed-stat">
          <span class="feed-stat-value">{{ categories.length - 1 }}</span>
          <span class="feed-stat-label">内容分类</span>
        </div>
        <div class="feed-stat">
          <span class="feed-stat-value">{{ activityBanner ? '1' : '0' }}</span>
          <span class="feed-stat-label">近期活动</span>
        </div>
        <div class="feed-stat">
          <span class="feed-stat-value">{{ hasMore ? '更多' : '当前' }}</span>
          <span class="feed-stat-label">内容状态</span>
        </div>
      </div>

      <p v-if="filterHint" class="filter-hint text-sm text-muted">{{ filterHint }}</p>
    </section>

    <div class="feed-toolbar-shell">
      <div class="category-bar" role="tablist" aria-label="帖子分类">
        <button v-for="cat in categories" :key="cat.key" class="cat-btn" :class="{ active: currentCategory === cat.key }" @click="switchCategory(cat.key)">
          {{ cat.label }}
        </button>
      </div>
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
      <div v-if="loading" class="feed-skeleton-list" aria-hidden="true">
        <div v-for="i in 3" :key="i" class="feed-skeleton card">
          <div class="feed-skeleton-head">
            <div class="skeleton-avatar"></div>
            <div class="skeleton-lines">
              <div class="skeleton-line skeleton-line-short"></div>
              <div class="skeleton-line skeleton-line-tiny"></div>
            </div>
          </div>
          <div class="skeleton-line skeleton-line-long"></div>
          <div class="skeleton-line skeleton-line-long"></div>
          <div class="skeleton-grid">
            <div class="skeleton-media" v-for="n in 2" :key="n"></div>
          </div>
        </div>
      </div>
      <template v-else-if="posts.length">
        <PostCard v-for="post in posts" :key="post._id" :post="post" :is-admin="isAdmin" @click="goDetail(post._id)" @avatar-click="onAvatarClick" />
        <div v-if="hasMore" class="load-more"><button class="btn btn-ghost btn-sm" @click="loadMore">加载更多</button></div>
      </template>
      <div v-else class="empty-state empty-feed-state">
        <div class="empty-feed-icon">云迹</div>
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
.feed-page {
  max-width: 760px;
  margin: 0 auto;
  padding: 14px 16px 24px;
}
.feed-hero {
  position: relative;
  padding: 18px 16px 16px;
  margin-bottom: 14px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,248,242,0.92));
  border: 1px solid rgba(255,130,0,0.08);
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.04);
}
.feed-hero-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.feed-kicker { font-size: 0.74rem; color: var(--primary); font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.page-title { font-size: 1.58rem; line-height: 1.15; font-weight: 800; letter-spacing: -0.02em; color: var(--text-primary); }
.hero-subtitle { font-size: 0.88rem; color: var(--text-muted); margin-top: 8px; line-height: 1.55; max-width: 32em; }
.hero-action {
  height: 38px;
  padding: 0 16px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(255,130,0,0.14), rgba(255,130,0,0.08));
  color: var(--primary);
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(255,130,0,0.12);
}
.search-entry {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 16px;
  border-radius: 18px;
  border: 1px solid rgba(255,130,0,0.12);
  background: rgba(255,255,255,0.88);
  cursor: pointer;
  text-align: left;
  font-size: 0.95rem;
  color: var(--text-muted);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 8px 18px rgba(17, 24, 39, 0.03);
}
.search-entry:hover, .search-entry:focus-visible {
  transform: translateY(-1px);
  border-color: rgba(255,130,0,0.28);
  box-shadow: 0 10px 22px rgba(255,130,0,0.08);
}
.search-entry-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: var(--primary);
  background: rgba(255,130,0,0.10);
  flex-shrink: 0;
}
.search-entry-text { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-entry-hint { font-size: 0.72rem; color: var(--text-muted); flex-shrink: 0; }
.feed-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.feed-stat {
  padding: 11px 10px;
  border-radius: 16px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(255,255,255,0.78);
}
.feed-stat-value { display: block; font-size: 1rem; font-weight: 800; color: var(--text-primary); }
.feed-stat-label { display: block; margin-top: 2px; font-size: 0.74rem; color: var(--text-muted); }
.filter-hint { margin-top: 10px; line-height: 1.45; }
.feed-toolbar-shell {
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 10px 0 12px;
  margin: 0 -16px 4px;
  background: linear-gradient(180deg, rgba(248,249,251,0.98), rgba(248,249,251,0.92));
  backdrop-filter: blur(14px);
}
.category-bar { display: flex; gap: 8px; overflow-x: auto; padding: 0 16px; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
.category-bar::-webkit-scrollbar { display: none; }
.cat-btn {
  flex-shrink: 0; padding: 8px 14px; border-radius: 999px;
  font-size: 0.84rem; background: rgba(255,255,255,0.92); border: 1px solid rgba(17,24,39,0.08);
  color: var(--text-secondary); transition: var(--transition); white-space: nowrap;
}
.cat-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); box-shadow: 0 10px 20px rgba(255,130,0,0.16); }
.post-list { margin-top: 6px; position: relative; }
.activity-feed-entry {
  width: 100%; display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; margin-bottom: 12px; border-radius: 18px;
  border: 1px solid rgba(255,130,0,0.10); background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,250,244,0.94)); cursor: pointer;
  text-align: left; font-family: inherit; transition: var(--transition);
}
.activity-feed-entry:hover { border-color: rgba(255,130,0,0.28); box-shadow: 0 10px 22px rgba(255,130,0,0.06); }
.activity-feed-icon { font-size: 0.78rem; color: var(--primary); font-weight: 700; flex-shrink: 0; }
.activity-feed-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.activity-feed-label { font-size: 0.72rem; color: var(--text-muted); }
.activity-feed-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.activity-feed-arrow { font-size: 1.2rem; color: var(--text-muted); flex-shrink: 0; }
.refresh-strip {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent); opacity: 0.8; animation: feed-refresh-pulse 1s ease-in-out infinite;
  z-index: 1; pointer-events: none;
}
.feed-skeleton-list { display: grid; gap: 12px; }
.feed-skeleton { padding: 16px; border-radius: 20px; }
.feed-skeleton-head { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; }
.skeleton-avatar, .skeleton-media, .skeleton-line, .skeleton-chip { background: linear-gradient(90deg, rgba(226,232,240,0.58), rgba(241,245,249,0.92), rgba(226,232,240,0.58)); background-size: 200% 100%; animation: shimmer 1.5s infinite linear; }
.skeleton-avatar { width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; }
.skeleton-lines { flex: 1; }
.skeleton-line { height: 12px; border-radius: 999px; }
.skeleton-line + .skeleton-line { margin-top: 8px; }
.skeleton-line-short { width: 38%; }
.skeleton-line-tiny { width: 26%; height: 10px; }
.skeleton-line-long { width: 100%; margin-bottom: 8px; }
.skeleton-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 10px; }
.skeleton-media { aspect-ratio: 1; border-radius: 12px; }
.skeleton-metrics { display: flex; gap: 8px; margin-top: 14px; }
.skeleton-chip { display: inline-block; height: 28px; width: 68px; border-radius: 999px; }
.empty-feed-state {
  padding: 40px 20px;
  text-align: center;
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,250,244,0.90));
  border: 1px dashed rgba(255,130,0,0.18);
  border-radius: 24px;
}
.empty-feed-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 72px; height: 72px; border-radius: 24px; margin-bottom: 12px;
  background: rgba(255,130,0,0.08); color: var(--primary); font-weight: 800;
}
.refresh-strip {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent); opacity: 0.8; animation: feed-refresh-pulse 1s ease-in-out infinite;
  z-index: 1; pointer-events: none;
}
@keyframes feed-refresh-pulse { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.load-more { text-align: center; padding: 16px; }
@media (min-width: 768px) {
  .feed-page { padding: 24px 32px 28px; }
  .feed-hero { padding: 24px 22px 20px; }
  .page-title { font-size: 1.92rem; }
  .hero-subtitle { font-size: 0.95rem; }
  .search-entry { padding: 14px 18px; }
}
@media (max-width: 480px) {
  .feed-page { padding: 12px 12px 20px; }
  .feed-hero { padding: 16px 14px 14px; border-radius: 20px; }
  .feed-hero-top { margin-bottom: 12px; }
  .page-title { font-size: 1.28rem; }
  .hero-subtitle { font-size: 0.83rem; margin-top: 7px; }
  .feed-stats { gap: 8px; }
  .feed-stat { padding: 10px 8px; border-radius: 14px; }
  .feed-stat-value { font-size: 0.96rem; }
  .feed-stat-label { font-size: 0.7rem; }
  .feed-toolbar-shell { margin: 0 -12px 4px; }
  .category-bar { padding: 0 12px; }
  .search-entry-hint { display: none; }
}
</style>

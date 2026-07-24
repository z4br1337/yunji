<template>
  <div class="feed-page">
    <!-- 顶栏：参考微博搜索区，简洁高级 -->
    <header class="feed-topbar">
      <div class="topbar-inner">
        <div class="topbar-brand" @click="scrollTop">
          <span class="brand-dot">云</span>
          <span class="brand-name">云迹广场</span>
        </div>
        <button type="button" class="topbar-search" @click="goSearch" aria-label="搜索">
          <span class="search-ico" aria-hidden="true">⌕</span>
          <span class="search-placeholder">{{ searchPlaceholder }}</span>
        </button>
        <div class="topbar-actions">
          <button type="button" class="topbar-btn ghost" @click="goSearch">搜索</button>
          <button type="button" class="topbar-btn primary" @click="goPublish">发帖</button>
        </div>
      </div>
    </header>

    <div class="feed-body">
      <!-- 桌面左侧：分类导航（微博式侧栏） -->
      <aside class="feed-side feed-side-left" aria-label="内容分类">
        <nav class="side-nav">
          <button
            v-for="cat in categories"
            :key="cat.key"
            type="button"
            class="side-nav-item"
            :class="{ active: currentCategory === cat.key }"
            @click="switchCategory(cat.key)"
          >
            <span class="side-nav-dot" aria-hidden="true"></span>
            {{ cat.label }}
          </button>
        </nav>
        <button v-if="activityBanner" type="button" class="side-activity" @click="goActivity">
          <span class="side-activity-label">近期活动</span>
          <span class="side-activity-title">{{ activityBanner.title }}</span>
        </button>
      </aside>

      <!-- 中间：信息流 -->
      <main class="feed-main">
        <div class="feed-tabs" role="tablist" aria-label="信息流频道">
          <button
            v-for="cat in categories"
            :key="'tab-' + cat.key"
            type="button"
            role="tab"
            class="feed-tab"
            :class="{ active: currentCategory === cat.key }"
            :aria-selected="currentCategory === cat.key"
            @click="switchCategory(cat.key)"
          >
            {{ cat.label }}
          </button>
        </div>

        <p v-if="filterHint" class="filter-hint">{{ filterHint }}</p>

        <div class="composer-card" @click="goPublish">
          <div class="composer-avatar">
            <img v-if="userAvatar" :src="userAvatar" alt="" />
            <span v-else>{{ userInitial }}</span>
          </div>
          <div class="composer-input">有什么想分享给同学们的？</div>
          <button type="button" class="composer-cta" @click.stop="goPublish">发布</button>
        </div>

        <div class="post-stream">
          <div v-if="refreshing" class="refresh-strip" aria-hidden="true" title="正在更新"></div>

          <button v-if="activityBanner" type="button" class="activity-strip mobile-only" @click="goActivity">
            <span class="activity-strip-badge">活动</span>
            <span class="activity-strip-title">{{ activityBanner.title }}</span>
            <span class="activity-strip-arrow">›</span>
          </button>

          <div v-if="loading" class="feed-skeleton-list" aria-hidden="true">
            <div v-for="i in 3" :key="i" class="feed-skeleton">
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
            <PostCard
              v-for="post in posts"
              :key="post._id"
              :post="post"
              :is-admin="isAdmin"
              @click="goDetail(post._id)"
              @avatar-click="onAvatarClick"
            />
            <div v-if="hasMore" class="load-more">
              <button type="button" class="btn-load-more" @click="loadMore">加载更多</button>
            </div>
          </template>

          <div v-else class="empty-feed">
            <div class="empty-feed-icon">云</div>
            <p class="empty-feed-title">还没有内容</p>
            <p class="empty-feed-desc">成为第一个在广场发声的人</p>
            <button type="button" class="btn btn-primary btn-sm" @click="goPublish">去发布</button>
          </div>
        </div>
      </main>

      <!-- 桌面右侧：热门 / 发现（微博式） -->
      <aside class="feed-side feed-side-right" aria-label="发现与热门">
        <section class="discover-card">
          <h3 class="discover-title">发现云迹</h3>
          <p class="discover-desc">校园动态、话题与闪光时刻，一站聚合。</p>
          <button type="button" class="discover-cta" @click="goPublish">发布内容</button>
        </section>

        <section class="hot-card">
          <div class="hot-card-head">
            <h3 class="hot-card-title">热门话题</h3>
            <button type="button" class="hot-card-more" @click="goSearch">更多</button>
          </div>
          <ul v-if="hotTopics.length" class="hot-list">
            <li
              v-for="(t, i) in hotTopics"
              :key="t"
              class="hot-item"
              @click="goTopic(t)"
            >
              <span class="hot-rank" :class="rankClass(i)">{{ i + 1 }}</span>
              <span class="hot-text">#{{ t }}#</span>
            </li>
          </ul>
          <p v-else class="hot-empty">暂无热门话题</p>
        </section>

        <section v-if="hotPosts.length" class="hot-card">
          <div class="hot-card-head">
            <h3 class="hot-card-title">热门帖子</h3>
          </div>
          <ul class="hot-list">
            <li
              v-for="(row, i) in hotPosts"
              :key="row._id"
              class="hot-item hot-item-post"
              @click="goDetail(row._id)"
            >
              <span class="hot-rank" :class="rankClass(i)">{{ i + 1 }}</span>
              <span class="hot-text">{{ row.snippet }}</span>
            </li>
          </ul>
        </section>
      </aside>
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
const categories = [{ key: 'all', label: '推荐' }, ...POST_CATEGORIES]
const currentCategory = ref('all')
const searchKeyword = ref('')
const activeTopic = ref('')
const posts = ref([])
const loading = ref(false)
const refreshing = ref(false)
const page = ref(1)
const hasMore = ref(false)
const activityBanner = ref(null)
const hotTopics = ref([])
const hotPosts = ref([])
let loaded = false

const userAvatar = computed(() => state.userInfo?.avatarUrl || '')
const userInitial = computed(() => (state.userInfo?.nickname || '我')[0])

const searchPlaceholder = computed(() => {
  if (activeTopic.value) return `话题：#${activeTopic.value}#`
  if (searchKeyword.value) return `搜索：${searchKeyword.value}`
  return '搜索云迹'
})

const filterHint = computed(() => {
  const parts = []
  if (activeTopic.value) parts.push(`话题「#${activeTopic.value}#」`)
  if (searchKeyword.value) parts.push(`关键词「${searchKeyword.value}」`)
  if (!parts.length) return ''
  return `当前筛选：${parts.join(' · ')} · 点搜索可修改`
})

function rankClass(i) {
  if (i === 0) return 'rank-1'
  if (i === 1) return 'rank-2'
  if (i === 2) return 'rank-3'
  return ''
}

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

function goPublish() {
  router.push('/publish')
}

function goActivity() {
  router.push({ name: 'ActivityList' })
}

function goTopic(t) {
  const name = String(t || '').trim()
  if (!name) return
  router.push({ path: '/feed', query: { topic: name } })
}

function scrollTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

async function loadHotPanels() {
  try {
    const [topicsRes, postsRes] = await Promise.all([
      api.getHotTopics().catch(() => ({ topics: [] })),
      api.getHotPostSnippets().catch(() => ({ posts: [] })),
    ])
    hotTopics.value = (topicsRes.topics || []).slice(0, 8)
    hotPosts.value = (postsRes.posts || []).slice(0, 6)
  } catch {
    hotTopics.value = []
    hotPosts.value = []
  }
}

onMounted(() => {
  syncQueryFromRoute()
  loadActivityBanner()
  loadHotPanels()
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
    if (p === '/feed') {
      loadActivityBanner()
      loadHotPanels()
    }
  }
)
</script>

<style scoped>
/* —— 整体：浅灰底 + 三栏信息流（微博式，品牌色保留橙系） —— */
.feed-page {
  min-height: 100%;
  background: #f0f2f5;
  padding-bottom: 24px;
}

/* 顶栏 */
.feed-topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.topbar-inner {
  max-width: 1180px;
  margin: 0 auto;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  cursor: pointer;
  user-select: none;
}
.brand-dot {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #ff8a1f, #ff6200);
  color: #fff;
  font-size: 0.85rem;
  font-weight: 800;
}
.brand-name {
  font-size: 1rem;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: 0.02em;
}
.topbar-search {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: #f5f6f8;
  color: #8a8f98;
  text-align: left;
  font-size: 0.9rem;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
}
.topbar-search:hover,
.topbar-search:focus-visible {
  background: #fff;
  border-color: rgba(255, 130, 0, 0.35);
  box-shadow: 0 0 0 3px rgba(255, 130, 0, 0.08);
}
.search-ico {
  font-size: 1.05rem;
  color: #ff7a00;
  flex-shrink: 0;
}
.search-placeholder {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.topbar-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 0.86rem;
  font-weight: 700;
  font-family: inherit;
  border: none;
  cursor: pointer;
}
.topbar-btn.ghost {
  background: transparent;
  color: #555;
}
.topbar-btn.ghost:hover { color: #ff7a00; }
.topbar-btn.primary {
  background: linear-gradient(135deg, #ff8a1f, #ff6200);
  color: #fff;
  box-shadow: 0 6px 14px rgba(255, 98, 0, 0.22);
}
.topbar-btn.primary:hover { filter: brightness(1.05); }

/* 三栏主体 */
.feed-body {
  max-width: 1180px;
  margin: 0 auto;
  padding: 16px;
  display: grid;
  grid-template-columns: 200px minmax(0, 1fr) 280px;
  gap: 16px;
  align-items: start;
}

/* 侧栏通用 */
.feed-side {
  position: sticky;
  top: 68px;
}
.side-nav {
  background: #fff;
  border-radius: 16px;
  padding: 8px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}
.side-nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: #333;
  font-size: 0.92rem;
  font-weight: 600;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.side-nav-item:hover { background: #f7f8fa; }
.side-nav-item.active {
  background: rgba(255, 130, 0, 0.1);
  color: #ff6200;
}
.side-nav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d0d4db;
  flex-shrink: 0;
}
.side-nav-item.active .side-nav-dot { background: #ff6200; }
.side-activity {
  margin-top: 12px;
  width: 100%;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(255, 130, 0, 0.12);
  background: linear-gradient(160deg, #fff9f3, #fff);
  text-align: left;
  cursor: pointer;
  font-family: inherit;
}
.side-activity-label {
  display: block;
  font-size: 0.72rem;
  color: #ff7a00;
  font-weight: 700;
  margin-bottom: 4px;
}
.side-activity-title {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.35;
}

/* 主列 */
.feed-main { min-width: 0; }
.feed-tabs {
  display: none;
  gap: 4px;
  overflow-x: auto;
  padding: 4px 0 12px;
  margin: 0 -4px 4px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.feed-tabs::-webkit-scrollbar { display: none; }
.feed-tab {
  flex-shrink: 0;
  padding: 8px 14px;
  border-radius: 999px;
  border: none;
  background: #fff;
  color: #666;
  font-size: 0.86rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.feed-tab.active {
  background: linear-gradient(135deg, #ff8a1f, #ff6200);
  color: #fff;
  box-shadow: 0 6px 14px rgba(255, 98, 0, 0.2);
}
.filter-hint {
  font-size: 0.8rem;
  color: #8a8f98;
  margin-bottom: 10px;
  line-height: 1.4;
}

/* 发帖入口条 */
.composer-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.composer-card:hover { box-shadow: 0 8px 22px rgba(0, 0, 0, 0.06); }
.composer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(145deg, #ff8a1f, #ff6200);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}
.composer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.composer-input {
  flex: 1;
  min-width: 0;
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 999px;
  background: #f5f6f8;
  color: #9aa0a8;
  font-size: 0.9rem;
}
.composer-cta {
  flex-shrink: 0;
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #ff8a1f, #ff6200);
  color: #fff;
  font-weight: 700;
  font-size: 0.86rem;
  font-family: inherit;
  cursor: pointer;
}

/* 信息流 */
.post-stream { position: relative; }
.activity-strip {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-bottom: 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 130, 0, 0.12);
  background: #fff;
  text-align: left;
  font-family: inherit;
  cursor: pointer;
}
.activity-strip-badge {
  font-size: 0.72rem;
  font-weight: 800;
  color: #ff6200;
  background: rgba(255, 130, 0, 0.1);
  padding: 2px 8px;
  border-radius: 999px;
}
.activity-strip-title {
  flex: 1;
  min-width: 0;
  font-size: 0.9rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.activity-strip-arrow { color: #bbb; font-size: 1.1rem; }
.mobile-only { display: none; }

.refresh-strip {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #ff7a00, transparent);
  animation: feed-pulse 1s ease-in-out infinite;
  z-index: 1;
  pointer-events: none;
}
@keyframes feed-pulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}

.feed-skeleton-list { display: grid; gap: 12px; }
.feed-skeleton {
  padding: 16px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.04);
}
.feed-skeleton-head {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.skeleton-avatar,
.skeleton-media,
.skeleton-line {
  background: linear-gradient(90deg, #eef0f3, #f7f8fa, #eef0f3);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite linear;
}
.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}
.skeleton-lines { flex: 1; }
.skeleton-line {
  height: 12px;
  border-radius: 999px;
}
.skeleton-line + .skeleton-line { margin-top: 8px; }
.skeleton-line-short { width: 36%; }
.skeleton-line-tiny { width: 22%; height: 10px; }
.skeleton-line-long { width: 100%; margin-bottom: 8px; }
.skeleton-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}
.skeleton-media {
  aspect-ratio: 1;
  border-radius: 10px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.load-more {
  text-align: center;
  padding: 16px 0 8px;
}
.btn-load-more {
  height: 40px;
  padding: 0 28px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #fff;
  color: #555;
  font-size: 0.88rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
}
.btn-load-more:hover {
  border-color: rgba(255, 130, 0, 0.35);
  color: #ff6200;
}

.empty-feed {
  text-align: center;
  padding: 48px 20px;
  background: #fff;
  border-radius: 16px;
  border: 1px dashed rgba(0, 0, 0, 0.08);
}
.empty-feed-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 130, 0, 0.1);
  color: #ff6200;
  font-weight: 800;
  font-size: 1.1rem;
}
.empty-feed-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 4px;
}
.empty-feed-desc {
  font-size: 0.86rem;
  color: #8a8f98;
  margin-bottom: 14px;
}

/* 右侧发现 / 热门 */
.discover-card {
  padding: 20px 18px;
  border-radius: 16px;
  background: linear-gradient(165deg, #fff6ec 0%, #ffffff 55%);
  border: 1px solid rgba(255, 130, 0, 0.1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
  margin-bottom: 12px;
  text-align: center;
}
.discover-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 6px;
}
.discover-desc {
  font-size: 0.82rem;
  color: #7a8088;
  line-height: 1.5;
  margin-bottom: 14px;
}
.discover-cta {
  width: 100%;
  height: 40px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff8a1f, #ff6200);
  color: #fff;
  font-weight: 800;
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(255, 98, 0, 0.22);
}
.discover-cta:hover { filter: brightness(1.04); }

.hot-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 12px 10px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
  margin-bottom: 12px;
}
.hot-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6px 10px;
}
.hot-card-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: #1a1a1a;
}
.hot-card-more {
  border: none;
  background: none;
  color: #8a8f98;
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
}
.hot-card-more:hover { color: #ff6200; }
.hot-list { list-style: none; margin: 0; padding: 0; }
.hot-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.12s;
}
.hot-item:hover { background: #f7f8fa; }
.hot-rank {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 800;
  color: #9aa0a8;
  background: #f0f2f5;
  flex-shrink: 0;
}
.hot-rank.rank-1 { background: #ffefe0; color: #ff6200; }
.hot-rank.rank-2 { background: #fff4e5; color: #e67e22; }
.hot-rank.rank-3 { background: #fff8ee; color: #d4a017; }
.hot-text {
  flex: 1;
  min-width: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: #222;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hot-item-post .hot-text { font-weight: 500; color: #444; }
.hot-empty {
  padding: 16px 8px;
  text-align: center;
  font-size: 0.84rem;
  color: #9aa0a8;
}

/* 桌面：侧栏随 App 侧栏偏移时的可读宽度 */
@media (min-width: 1100px) {
  .topbar-inner,
  .feed-body { max-width: 1120px; }
}

/* 平板：隐藏左右侧栏，保留顶栏 + 横向 tabs */
@media (max-width: 1024px) {
  .feed-body {
    grid-template-columns: 1fr;
    max-width: 720px;
  }
  .feed-side-left,
  .feed-side-right { display: none; }
  .feed-tabs { display: flex; }
  .mobile-only { display: flex; }
}

/* 手机 */
@media (max-width: 768px) {
  .feed-page { padding-bottom: calc(var(--tabbar-h, 56px) + 12px); }
  .topbar-inner { padding: 8px 12px; gap: 10px; }
  .brand-name { display: none; }
  .topbar-btn.ghost { display: none; }
  .topbar-btn.primary {
    padding: 0 12px;
    height: 34px;
    font-size: 0.82rem;
  }
  .topbar-search { height: 36px; font-size: 0.86rem; }
  .feed-body { padding: 10px 12px 16px; gap: 0; }
  .composer-card { padding: 12px; border-radius: 14px; }
  .composer-cta { display: none; }
  .composer-input { font-size: 0.86rem; height: 36px; }
  .composer-avatar { width: 36px; height: 36px; }
  .feed-tab { padding: 7px 12px; font-size: 0.82rem; }
}

@media (max-width: 480px) {
  .topbar-inner { padding: 8px 10px; }
  .feed-body { padding: 8px 10px 14px; }
  .discover-card,
  .hot-card { border-radius: 14px; }
}

/* 桌面有 App 侧栏时，顶栏与内容对齐主区 */
@media (min-width: 768px) {
  :global(.is-desktop .main-content.with-sidebar) .feed-topbar {
    /* 顶栏在主内容区内 sticky 即可 */
  }
}
</style>

<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>我的帖子</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <!-- Tabs: 已发布 / 已封存 -->
    <div class="section-tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'published' }" @click="activeTab = 'published'">
        已发布 ({{ publishedCount }})
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'archived' }" @click="activeTab = 'archived'">
        已封存 ({{ archivedCount }})
      </button>
    </div>

    <div class="post-list-wrap">
      <div v-if="refreshing" class="refresh-strip" aria-hidden="true" title="正在更新"></div>
      <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else>
        <div v-if="displayPosts.length" class="post-list">
          <div v-for="post in displayPosts" :key="post._id" class="post-row">
            <PostCard class="post-row-card" :post="post" :is-admin="false"
              @click="goDetail(post._id)" />
            <button type="button" class="btn btn-danger btn-sm post-row-del" @click.stop="onDeletePost(post)">删除</button>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="icon">📭</div>
          <div class="text">{{ activeTab === 'archived' ? '暂无已封存帖子' : '暂无已发布帖子' }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'
import * as localPostCache from '../utils/localPostCache.js'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const showToast = inject('showToast')
const activeTab = ref('published')
const allPosts = ref([])
const archivedPosts = ref([])
const loading = ref(false)
const refreshing = ref(false)

const publishedCount = computed(() => allPosts.value.length)
const archivedCount = computed(() => archivedPosts.value.length)

const displayPosts = computed(() => {
  return activeTab.value === 'archived' ? archivedPosts.value : allPosts.value
})

async function fetchAllMyPostsFromNetwork() {
  let p = 1
  let more = true
  const published = []
  const archived = []
  while (more) {
    const result = await api.getPosts({
      myPosts: true,
      excludeEmotion: true,
      page: p,
      pageSize: 50,
    })
    const posts = result.posts || []
    posts.forEach((po) => {
      if (po.status === 'archived') archived.push(po)
      else published.push(po)
    })
    more = result.hasMore || false
    p++
  }
  return { published, archived }
}

async function loadBoth() {
  const snap = localPostCache.getMyPostsSnapshot()
  const hadCache = !!(snap?.published?.length || snap?.archived?.length)
  if (hadCache) {
    allPosts.value = snap.published
    archivedPosts.value = snap.archived
    loading.value = false
    refreshing.value = true
  } else {
    loading.value = true
    refreshing.value = false
  }

  try {
    const { published, archived } = await fetchAllMyPostsFromNetwork()
    allPosts.value = published
    archivedPosts.value = archived
    localPostCache.saveMyPostsSnapshot(published, archived)
  } catch (e) {
    if (!hadCache) {
      allPosts.value = []
      archivedPosts.value = []
      showToast(e.message || '加载失败')
    } else {
      showToast('网络异常，暂显示本地缓存')
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function goDetail(id) {
  router.push(`/post/${id}`)
}

async function onDeletePost(post) {
  if (!window.confirm('确定删除该帖子？删除后不可恢复。')) return
  try {
    await api.deletePost(post._id)
    localPostCache.invalidateReadPost(post._id)
    localPostCache.removePostFromAllFeedSnapshots(post._id)
    localPostCache.removePostFromMyPostsSnapshot(post._id)
    showToast('已删除')
    await loadBoth()
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

onMounted(() => loadBoth())
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.section-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab-btn {
  padding: 8px 16px; border-radius: var(--radius-sm);
  font-size: 0.9rem; background: var(--bg); border: 1px solid var(--border);
  color: var(--text-secondary); transition: var(--transition);
}
.tab-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.post-list-wrap { position: relative; }
.refresh-strip {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  animation: myposts-refresh-pulse 1s ease-in-out infinite;
  z-index: 1; pointer-events: none;
}
@keyframes myposts-refresh-pulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}
.load-more { text-align: center; padding: 16px; }
.post-row {
  display: flex; align-items: stretch; gap: 10px; margin-bottom: 12px;
}
.post-row-card { flex: 1; min-width: 0; }
.post-row-del { flex-shrink: 0; align-self: center; }
</style>

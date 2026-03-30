<template>
  <div class="page-container personal-home">
    <div class="page-header flex justify-between items-center">
      <h2>个人主页</h2>
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <!-- 头图区（参考贴吧个人信息条） -->
    <div class="ph-header card mb-12" v-if="user">
      <div class="ph-header-inner flex items-start gap-16">
        <div class="avatar avatar-lg">
          <img v-if="user.avatarUrl" :src="user.avatarUrl" alt="" />
          <span v-else>{{ (user.nickname || '?')[0] }}</span>
        </div>
        <div class="ph-header-text flex-1">
          <div class="flex items-center gap-8 flex-wrap">
            <h3 class="ph-name">{{ user.nickname }}</h3>
            <span class="ph-level">Lv{{ levelInfo.level }} {{ levelInfo.title }}</span>
          </div>
          <p class="text-sm text-secondary mt-4">{{ user.class || '未填写班级' }}</p>
          <div class="badge-row flex gap-8 mt-8">
            <span
              v-for="b in badges"
              :key="b.type"
              class="badge"
              :style="{ background: b.color + '18', color: b.color }"
            >{{ b.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="ph-tabs" role="tablist">
      <button
        type="button"
        class="ph-tab"
        :class="{ active: tab === 'overview' }"
        @click="tab = 'overview'"
      >概览</button>
      <button
        type="button"
        class="ph-tab"
        :class="{ active: tab === 'posts' }"
        @click="tab = 'posts'"
      >动态</button>
      <button
        type="button"
        class="ph-tab"
        :class="{ active: tab === 'growth' }"
        @click="tab = 'growth'"
      >成长手册</button>
    </div>

    <div v-show="tab === 'overview'" class="ph-panel">
      <div class="card mb-12">
        <div class="profile-stats flex justify-between">
          <div class="stat-item text-center">
            <div class="stat-num">{{ user?.exp || 0 }}</div>
            <div class="stat-label text-xs text-muted">经验值</div>
          </div>
          <div class="stat-item text-center">
            <div class="stat-num">{{ user?.score || 0 }}</div>
            <div class="stat-label text-xs text-muted">积分</div>
          </div>
          <div class="stat-item text-center clickable" @click="tab = 'posts'">
            <div class="stat-num">{{ user?.postCount || 0 }}</div>
            <div class="stat-label text-xs text-muted">帖子</div>
          </div>
          <div class="stat-item text-center clickable" @click="$router.push('/my-files')">
            <div class="stat-num">{{ fileShareCount }}</div>
            <div class="stat-label text-xs text-muted">分享文件</div>
          </div>
        </div>
        <div class="exp-bar mt-16">
          <div class="exp-fill" :style="{ width: (levelInfo.progress * 100) + '%' }"></div>
        </div>
        <p class="text-xs text-muted mt-8" v-if="user && !levelInfo.isMax">
          距下一级还需 {{ levelInfo.expToNext - levelInfo.expInLevel }} 经验
        </p>
      </div>
      <p class="text-xs text-muted ph-tip">在「动态」查看帖子，在「成长手册」管理闪光时刻与公开设置</p>
    </div>

    <div v-show="tab === 'posts'" class="ph-panel">
      <div v-if="postsLoading" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="myPostList.length">
        <PostCard
          v-for="p in myPostList"
          :key="p._id"
          :post="p"
          :is-admin="isAdmin"
          @click="goPost(p._id)"
        />
      </template>
      <div v-else class="empty-state text-muted text-sm">暂无已发布帖子</div>
    </div>

    <div v-show="tab === 'growth'" class="ph-panel ph-growth-embed">
      <GrowthBook embedded />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { getLevelInfo, getUserBadges } from '../utils/level.js'
import * as api from '../api/index.js'
import PostCard from '../components/PostCard.vue'
import GrowthBook from './GrowthBook.vue'

const router = useRouter()
const { state, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const user = computed(() => state.userInfo)
const isAdmin = computed(() => state.isAdmin)
const levelInfo = computed(() => getLevelInfo(user.value?.exp))
const badges = computed(() => {
  const b = user.value ? getUserBadges(user.value) : []
  return b.filter((x) => x.type !== 'level')
})

const tab = ref('overview')
const myPostList = ref([])
const postsLoading = ref(false)
const fileShareCount = ref(0)

async function loadPosts() {
  postsLoading.value = true
  try {
    const r = await api.getPosts({
      myPosts: true,
      excludeEmotion: true,
      page: 1,
      pageSize: 50,
    })
    const posts = r.posts || []
    myPostList.value = posts.filter((p) => p.status !== 'archived')
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    postsLoading.value = false
  }
}

async function loadFileCount() {
  try {
    const r = await api.getFileShareList({ myFiles: true, pageSize: 1 })
    fileShareCount.value = r.total || 0
  } catch { /* ignore */ }
}

function goPost(id) {
  router.push(`/post/${id}`)
}

onMounted(async () => {
  try {
    await refreshProfile()
  } catch { /* ignore */ }
  await loadFileCount()
})

watch(tab, (t) => {
  if (t === 'posts' && !myPostList.value.length && !postsLoading.value) loadPosts()
})

watch(() => state.userInfo?.postCount, () => {
  if (tab.value === 'posts') loadPosts()
})
</script>

<style scoped>
.page-container { max-width: 640px; margin: 0 auto; padding: 16px; }
.personal-home { padding-bottom: 24px; }
.ph-header {
  background: linear-gradient(135deg, rgba(126, 200, 227, 0.2), rgba(74, 144, 217, 0.12));
  border: 1px solid var(--border);
}
.ph-header-inner { padding: 4px 0; }
.ph-name { margin: 0; font-size: 1.2rem; }
.ph-level {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 100px;
  background: rgba(74, 144, 217, 0.15);
  color: var(--primary);
  font-weight: 600;
}
.ph-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.ph-tab {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 8px 12px;
  font-size: 0.9rem;
  color: var(--text-muted);
  cursor: pointer;
  position: relative;
  font-weight: 500;
}
.ph-tab.active {
  color: var(--primary);
  font-weight: 700;
}
.ph-tab.active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  width: 36px;
  height: 3px;
  background: var(--primary);
  border-radius: 2px;
}
.ph-panel { min-height: 120px; }
.ph-tip { margin-top: 8px; line-height: 1.5; }
.ph-growth-embed :deep(.page-container) {
  padding-left: 0;
  padding-right: 0;
}
.ph-growth-embed :deep(.page-header) {
  display: none;
}
.profile-stats { flex-wrap: wrap; gap: 12px; }
.stat-item { min-width: 72px; }
.stat-item.clickable { cursor: pointer; }
.stat-num { font-size: 1.2rem; font-weight: 700; }
.exp-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.exp-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--primary-light)); border-radius: 3px; }
</style>

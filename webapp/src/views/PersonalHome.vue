<template>
  <div class="page-container personal-home">
    <div class="page-header flex justify-between items-center">
      <h2>{{ pageTitle }}</h2>
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="profileLoading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="profileUser">
      <!-- 头图区 -->
      <div class="ph-header card mb-12">
        <div class="ph-header-inner flex items-start gap-16">
          <div class="avatar avatar-lg">
            <img v-if="profileUser.avatarUrl" :src="profileUser.avatarUrl" alt="" />
            <span v-else>{{ (profileUser.nickname || '?')[0] }}</span>
          </div>
          <div class="ph-header-text flex-1">
            <div class="flex items-center gap-8 flex-wrap">
              <h3 class="ph-name">{{ profileUser.nickname }}</h3>
              <span class="ph-level">Lv{{ levelInfo.level }} {{ levelInfo.title }}</span>
            </div>
            <p class="text-sm text-secondary mt-4">{{ profileUser.class || '未填写班级' }}</p>
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
        <button
          v-if="!isMe && profileUser._id"
          type="button"
          class="btn btn-primary btn-sm ph-btn-dm"
          @click="goDm"
        >✈️ 发私信</button>
      </div>

      <div class="ph-tabs" role="tablist">
        <button type="button" class="ph-tab" :class="{ active: tab === 'overview' }" @click="tab = 'overview'">概览</button>
        <button type="button" class="ph-tab" :class="{ active: tab === 'posts' }" @click="tab = 'posts'">动态</button>
        <button type="button" class="ph-tab" :class="{ active: tab === 'growth' }" @click="tab = 'growth'">成长手册</button>
      </div>

      <div v-show="tab === 'overview'" class="ph-panel">
        <div class="card mb-12">
          <div class="profile-stats flex justify-between">
            <div class="stat-item text-center">
              <div class="stat-num">{{ profileUser.exp || 0 }}</div>
              <div class="stat-label text-xs text-muted">经验值</div>
            </div>
            <div class="stat-item text-center">
              <div class="stat-num">{{ profileUser.score || 0 }}</div>
              <div class="stat-label text-xs text-muted">积分</div>
            </div>
            <div class="stat-item text-center clickable" @click="tab = 'posts'">
              <div class="stat-num">{{ profileUser.postCount || 0 }}</div>
              <div class="stat-label text-xs text-muted">帖子</div>
            </div>
            <div
              class="stat-item text-center"
              :class="{ clickable: isMe }"
              @click="isMe && $router.push('/my-files')"
            >
              <div class="stat-num">{{ fileShareCount }}</div>
              <div class="stat-label text-xs text-muted">分享文件</div>
            </div>
          </div>
          <div class="exp-bar mt-16">
            <div class="exp-fill" :style="{ width: (levelInfo.progress * 100) + '%' }"></div>
          </div>
          <p class="text-xs text-muted mt-8" v-if="!levelInfo.isMax">
            距下一级还需 {{ levelInfo.expToNext - levelInfo.expInLevel }} 经验
          </p>
        </div>

        <!-- 留言板 -->
        <div class="card wall-card">
          <h3 class="wall-title">留言板</h3>
          <p class="text-xs text-muted mb-12">导生留言置顶显示；主人可删除普通用户留言，导生可删除全部留言。</p>
          <div class="wall-compose flex flex-col gap-8">
            <textarea
              v-model="wallDraft"
              class="form-textarea"
              rows="2"
              maxlength="500"
              placeholder="写一句留言…"
            />
            <button type="button" class="btn btn-primary btn-sm self-end" :disabled="!wallDraft.trim() || wallSending" @click="submitWall">
              {{ wallSending ? '发送中…' : '发表留言' }}
            </button>
          </div>
          <div v-if="wallLoading" class="loading-spinner wall-loading"><div class="spinner"></div></div>
          <ul v-else class="wall-list">
            <li v-for="m in wallMessages" :key="m._id" class="wall-item">
              <div class="flex items-center gap-8 mb-4">
                <span class="font-bold text-sm">{{ m.authorName }}</span>
                <span v-if="m.isAdmin" class="badge badge-danger">导生</span>
                <span class="text-xs text-muted" style="margin-left:auto">{{ m.createdAt }}</span>
              </div>
              <p class="text-sm wall-content">{{ m.content }}</p>
              <button
                v-if="canDeleteWall(m)"
                type="button"
                class="btn btn-ghost btn-sm wall-del mt-8"
                @click="removeWall(m)"
              >删除</button>
            </li>
          </ul>
          <p v-if="!wallLoading && !wallMessages.length" class="text-muted text-sm text-center py-16">暂无留言</p>
        </div>

        <p class="text-xs text-muted ph-tip">在「动态」查看帖子，在「成长手册」查看闪光时刻（公开时）</p>
      </div>

      <div v-show="tab === 'posts'" class="ph-panel">
        <div v-if="postsLoading" class="loading-spinner"><div class="spinner"></div></div>
        <template v-else-if="userPostList.length">
          <PostCard
            v-for="p in userPostList"
            :key="p._id"
            :post="p"
            :is-admin="isAdmin"
            @click="goPost(p._id)"
          />
        </template>
        <div v-else class="empty-state text-muted text-sm">暂无已发布帖子</div>
      </div>

      <div v-show="tab === 'growth'" class="ph-panel ph-growth-embed">
        <GrowthBook embedded :target-user-id="targetUserId" />
      </div>
    </template>

    <div v-else class="empty-state text-muted">无法加载用户资料</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { getLevelInfo, getUserBadges } from '../utils/level.js'
import * as api from '../api/index.js'
import PostCard from '../components/PostCard.vue'
import GrowthBook from './GrowthBook.vue'

const route = useRoute()
const router = useRouter()
const { state, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const isAdmin = computed(() => state.isAdmin)
const meId = computed(() => state.userInfo?._id || '')

const targetUserId = computed(() => {
  const p = route.params.userId
  if (p != null && String(p).trim() !== '') return String(p).trim()
  return meId.value || ''
})

const isMe = computed(() => !!(meId.value && targetUserId.value === meId.value))

const pageTitle = computed(() => {
  if (isMe.value) return '个人主页'
  const n = profileUser.value?.nickname
  return n ? `${n}的主页` : '个人主页'
})

const profileUser = ref(null)
const profileLoading = ref(true)
const fileShareCount = ref(0)

const levelInfo = computed(() => getLevelInfo(profileUser.value?.exp))
const badges = computed(() => {
  const u = profileUser.value
  if (!u) return []
  const b = getUserBadges(u)
  return b.filter((x) => x.type !== 'level')
})

const tab = ref('overview')
const userPostList = ref([])
const postsLoading = ref(false)

const wallMessages = ref([])
const wallLoading = ref(false)
const wallDraft = ref('')
const wallSending = ref(false)

function canDeleteWall(m) {
  if (isAdmin.value) return true
  if (isMe.value && !m.isAdmin) return true
  return false
}

async function loadPublicHome() {
  const uid = targetUserId.value
  if (!uid) {
    profileLoading.value = false
    profileUser.value = null
    return
  }
  profileLoading.value = true
  try {
    const r = await api.getUserPublicHome(uid)
    profileUser.value = r.user
    fileShareCount.value = r.fileShareCount ?? 0
  } catch (e) {
    showToast(e.message || '加载失败')
    profileUser.value = null
  } finally {
    profileLoading.value = false
  }
}

async function loadPosts() {
  const uid = targetUserId.value
  if (!uid) return
  postsLoading.value = true
  try {
    const r = await api.getPosts({
      authorId: uid,
      page: 1,
      pageSize: 50,
    })
    const posts = r.posts || []
    userPostList.value = posts.filter((p) => p.status !== 'archived')
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    postsLoading.value = false
  }
}

async function loadWall() {
  const uid = targetUserId.value
  if (!uid) return
  wallLoading.value = true
  try {
    const r = await api.getWallList(uid, 1, 50)
    wallMessages.value = r.messages || []
  } catch (e) {
    showToast(e.message || '留言加载失败')
  } finally {
    wallLoading.value = false
  }
}

async function submitWall() {
  const text = wallDraft.value.trim()
  if (!text || !targetUserId.value) return
  wallSending.value = true
  try {
    await api.addWallMessage(targetUserId.value, text)
    wallDraft.value = ''
    showToast('留言已发布')
    await loadWall()
  } catch (e) {
    showToast(e.message || '发送失败')
  } finally {
    wallSending.value = false
  }
}

async function removeWall(m) {
  if (!window.confirm('确定删除该留言？')) return
  try {
    await api.deleteWallMessage(m._id)
    showToast('已删除')
    await loadWall()
  } catch (e) {
    showToast(e.message || '删除失败')
  }
}

function goDm() {
  const u = profileUser.value
  if (!u?._id) return
  router.push(`/chat/${u._id}?name=${encodeURIComponent(u.nickname || '用户')}`)
}

function goPost(id) {
  router.push(`/post/${id}`)
}

onMounted(async () => {
  try {
    await refreshProfile()
  } catch { /* ignore */ }
  await loadPublicHome()
  await loadWall()
})

watch(targetUserId, async () => {
  await loadPublicHome()
  userPostList.value = []
  await loadWall()
  if (tab.value === 'posts') await loadPosts()
})

watch(tab, (t) => {
  if (t === 'posts' && !userPostList.value.length && !postsLoading.value) loadPosts()
})

watch(() => state.userInfo?.postCount, () => {
  if (tab.value === 'posts' && isMe.value) loadPosts()
})
</script>

<style scoped>
.page-container { max-width: 640px; margin: 0 auto; padding: 16px; }
.personal-home { padding-bottom: 24px; }
.ph-header {
  position: relative;
  background: linear-gradient(135deg, rgba(126, 200, 227, 0.2), rgba(74, 144, 217, 0.12));
  border: 1px solid var(--border);
  padding-bottom: 44px;
}
.ph-header-inner { padding: 4px 0; }
.ph-btn-dm {
  position: absolute;
  right: 12px;
  bottom: 12px;
}
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
.wall-card { margin-top: 0; }
.wall-title { font-size: 1rem; margin-bottom: 8px; }
.wall-list { list-style: none; margin: 16px 0 0; padding: 0; }
.wall-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.wall-item:last-child { border-bottom: none; }
.wall-content { white-space: pre-wrap; word-break: break-word; }
.wall-del { padding: 2px 10px; font-size: 0.75rem; }
.wall-loading { min-height: 48px; }
.self-end { align-self: flex-end; }
</style>

<template>
  <div class="admin-page">
    <div class="admin-header flex justify-between items-center">
      <h2>管理后台</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.push('/settings')">返回</button>
    </div>

    <!-- Tabs -->
    <div class="admin-tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tab-btn" :class="{ active: activeTab === tab.key }" @click="switchTab(tab.key)">
        {{ tab.label }}
      </button>
    </div>

    <!-- Achievement Review -->
    <div v-if="activeTab === 'achievements'" class="tab-panel">
      <div class="card mb-16">
        <h4 class="mb-8">审核参考标准</h4>
        <div v-for="g in reviewGuide" :key="g.level" class="guide-row text-sm flex gap-8 mb-4">
          <span class="guide-level badge badge-primary">等级{{ g.level }}</span>
          <span class="font-bold">{{ g.label }}</span>
          <span class="text-muted">{{ g.desc }}</span>
        </div>
      </div>
      <p class="text-sm text-muted mb-8">以下成果待你审核。通过后提交者将获得对应经验值。</p>

      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="pendingAchs.length">
        <div v-for="ach in pendingAchs" :key="ach._id" class="card mb-8">
          <div class="flex justify-between items-center mb-4">
            <span class="font-bold">{{ ach.title }}</span>
            <span class="badge badge-warning">待审核</span>
          </div>
          <p class="text-sm text-secondary">{{ ach.description }}</p>
          <p class="text-xs text-muted mt-4">分类: {{ achCatLabel(ach.category) }} | 等级: {{ ach.level }}</p>
          <div v-if="ach.images && ach.images.length" class="flex gap-8 mt-8">
            <img v-for="(img, i) in ach.images" :key="i" :src="img" style="width:60px;height:60px;object-fit:cover;border-radius:8px" />
          </div>
          <div class="flex gap-8 mt-8">
            <button class="btn btn-success btn-sm" @click="approveAch(ach._id)">通过</button>
            <button class="btn btn-danger btn-sm" @click="rejectAch(ach._id)">驳回</button>
          </div>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">✅</div><div class="text">暂无待审核成果</div></div>
    </div>

    <!-- Flagged Posts -->
    <div v-if="activeTab === 'flagged'" class="tab-panel">
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="flaggedPosts.length">
        <div v-for="p in flaggedPosts" :key="p._id" class="card mb-8 post-flagged">
          <div class="flex justify-between items-center mb-4">
            <span class="font-bold">{{ p.visibleAuthorName }}</span>
            <span class="badge badge-danger">⚠️ 违规</span>
          </div>
          <p class="text-sm" v-html="p.flaggedHighlighted || p.content"></p>
          <p class="text-xs text-muted mt-4">敏感词: {{ (p.flaggedWords || []).join(', ') }}</p>
          <div class="flex gap-8 mt-8">
            <button class="btn btn-success btn-sm" @click="overridePost(p._id, 'published')">恢复发布</button>
            <button class="btn btn-danger btn-sm" @click="overridePost(p._id, 'archived')">永久封存</button>
          </div>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">🛡️</div><div class="text">暂无违规帖子</div></div>
    </div>

    <!-- All Posts -->
    <div v-if="activeTab === 'allPosts'" class="tab-panel">
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="allPosts.length">
        <div v-for="p in allPosts" :key="p._id" class="card mb-8" :class="{ 'post-pinned': p.pinned }">
          <div class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-8">
              <span class="font-bold">{{ p.visibleAuthorName }}</span>
              <span v-if="p.pinned" class="badge badge-warning">📌 置顶</span>
            </div>
            <span class="badge" :class="'badge-' + (p.status === 'published' ? 'success' : 'warning')">{{ statusLabel(p.status) }}</span>
          </div>
          <p class="text-sm">{{ p.content && p.content.substring(0, 100) }}</p>
          <div class="flex gap-8 mt-8 flex-wrap">
            <button v-if="p.status !== 'archived'" class="btn btn-warning btn-sm" @click="overridePost(p._id, 'archived')">封存</button>
            <button v-if="p.status === 'archived'" class="btn btn-success btn-sm" @click="overridePost(p._id, 'published')">恢复</button>
            <button v-if="!p.pinned" class="btn btn-ghost btn-sm" @click="pinPost(p._id)">置顶</button>
            <button v-else class="btn btn-ghost btn-sm" @click="unpinPost(p._id)">取消置顶</button>
          </div>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">📄</div><div class="text">暂无帖子</div></div>
    </div>

    <!-- Users -->
    <div v-if="activeTab === 'users'" class="tab-panel">
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="users.length">
        <div v-for="u in users" :key="u._id" class="card mb-8 user-card" @click="$router.push(`/admin/user/${u._id}`)">
          <div class="flex items-center gap-12">
            <div class="avatar">{{ (u.nickname || '?')[0] }}</div>
            <div>
              <div class="font-bold">{{ u.nickname }}</div>
              <div class="text-xs text-muted">{{ u.class }} | {{ u.role === 'admin' ? '导生' : '用户' }} | Exp: {{ u.exp || 0 }}</div>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">👥</div><div class="text">暂无用户</div></div>
    </div>

    <!-- Pending File Shares -->
    <div v-if="activeTab === 'fileShare'" class="tab-panel">
      <p class="text-sm text-muted mb-8">以下文件分享待审核，通过后其他用户可见。</p>
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="pendingFiles.length">
        <div v-for="f in pendingFiles" :key="f._id" class="card mb-8">
          <h4 class="mb-4">{{ f.title }}</h4>
          <p v-if="f.description" class="text-sm text-secondary mb-4">{{ f.description }}</p>
          <p class="text-xs text-muted mb-8">{{ f.authorName }} · {{ f.fileName || '文件' }}</p>
          <button class="btn btn-success btn-sm" @click="approveFile(f._id)">通过</button>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">📁</div><div class="text">暂无待审核文件</div></div>
    </div>

    <!-- Shop Stock -->
    <div v-if="activeTab === 'shop'" class="tab-panel">
      <p class="text-sm text-muted mb-8">修改积分商店商品剩余数量。</p>
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="shopItems.length">
        <div v-for="item in shopItems" :key="item._id" class="card mb-8 flex justify-between items-center">
          <div>
            <h4>{{ item.title }}</h4>
            <p class="text-sm text-muted">{{ item.price }} 积分 · 剩余 {{ item.stock }}</p>
          </div>
          <div class="flex gap-8 items-center">
            <input type="number" class="form-input" v-model.number="item.editStock" min="0" style="width:80px" />
            <button class="btn btn-primary btn-sm" @click="updateStock(item)">保存</button>
          </div>
        </div>
      </template>
      <div v-else class="empty-state"><div class="icon">🛒</div><div class="text">暂无商品</div></div>
    </div>

    <!-- Invite -->
    <div v-if="activeTab === 'invite'" class="tab-panel">
      <div class="card">
        <h4 class="mb-8">生成邀请码</h4>
        <button class="btn btn-primary" :disabled="generating" @click="generateInvite">
          {{ generating ? '生成中...' : '生成新邀请码' }}
        </button>
        <div v-if="generatedCode" class="invite-result mt-16 card" style="background:#E8F5E9">
          <p class="font-bold">{{ generatedCode }}</p>
          <p class="text-sm text-muted">请复制给需要的用户</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { REVIEW_LEVEL_GUIDE, ACHIEVEMENT_CATEGORIES, POST_STATUS_LABELS } from '../../utils/config.js'
import * as api from '../../api/index.js'

const showToast = inject('showToast')
const reviewGuide = REVIEW_LEVEL_GUIDE

const achCatMap = {}
ACHIEVEMENT_CATEGORIES.forEach(c => { achCatMap[c.key] = c.label })
function achCatLabel(key) { return achCatMap[key] || key }
function statusLabel(s) { return POST_STATUS_LABELS[s] || s }

const tabs = [
  { key: 'achievements', label: '成果审核' },
  { key: 'flagged', label: '违规帖子' },
  { key: 'allPosts', label: '全部帖子' },
  { key: 'fileShare', label: '文件审核' },
  { key: 'shop', label: '积分商店' },
  { key: 'users', label: '用户' },
  { key: 'invite', label: '邀请码' }
]
const activeTab = ref('achievements')
const loadingTab = ref(false)

const pendingAchs = ref([])
const flaggedPosts = ref([])
const allPosts = ref([])
const pendingFiles = ref([])
const shopItems = ref([])
const users = ref([])
const generating = ref(false)
const generatedCode = ref('')

async function switchTab(key) {
  activeTab.value = key
  await loadTabData()
}

async function loadTabData() {
  loadingTab.value = true
  try {
    switch (activeTab.value) {
      case 'achievements': {
        const r = await api.adminGetPendingAchievements()
        pendingAchs.value = r.achievements || []
        break
      }
      case 'flagged': {
        const r = await api.adminGetReports()
        flaggedPosts.value = r.flagged || []
        break
      }
      case 'allPosts': {
        const r = await api.adminGetReports()
        allPosts.value = r.allPosts || []
        break
      }
      case 'fileShare': {
        const r = await api.adminGetPendingFileShares()
        pendingFiles.value = r.items || []
        break
      }
      case 'shop': {
        const r = await api.adminGetShopItems()
        shopItems.value = (r.items || []).map(i => ({ ...i, editStock: i.stock }))
        break
      }
      case 'users': {
        const r = await api.adminGetUserList()
        users.value = r.users || []
        break
      }
    }
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loadingTab.value = false
  }
}

async function approveAch(id) {
  try {
    await api.adminApproveAchievement(id)
    showToast('已通过')
    pendingAchs.value = pendingAchs.value.filter(a => a._id !== id)
  } catch (e) { showToast(e.message || '操作失败') }
}

async function rejectAch(id) {
  try {
    await api.adminRejectAchievement(id)
    showToast('已驳回')
    pendingAchs.value = pendingAchs.value.filter(a => a._id !== id)
  } catch (e) { showToast(e.message || '操作失败') }
}

async function overridePost(id, action) {
  try {
    await api.adminOverridePost(id, action)
    showToast('操作成功')
    await loadTabData()
  } catch (e) { showToast(e.message || '操作失败') }
}

async function pinPost(id) {
  await api.adminPinPost(id)
  showToast('已置顶')
  await loadTabData()
}

async function unpinPost(id) {
  await api.adminUnpinPost(id)
  showToast('已取消置顶')
  await loadTabData()
}

async function approveFile(id) {
  try {
    await api.adminApproveFileShare(id)
    showToast('已通过')
    pendingFiles.value = pendingFiles.value.filter(f => f._id !== id)
  } catch (e) { showToast(e.message || '操作失败') }
}

async function updateStock(item) {
  try {
    await api.adminUpdateShopStock(item.itemKey, item.editStock)
    showToast('已保存')
    item.stock = item.editStock
  } catch (e) { showToast(e.message || '操作失败') }
}

async function generateInvite() {
  generating.value = true
  try {
    const r = await api.adminGenerateInvite()
    generatedCode.value = r.inviteCode
    showToast('邀请码已生成')
  } catch (e) { showToast(e.message || '生成失败') }
  finally { generating.value = false }
}

onMounted(() => loadTabData())
</script>

<style scoped>
.admin-page { max-width: 800px; margin: 0 auto; padding: 16px; }
.admin-header { margin-bottom: 16px; }
.admin-tabs { display: flex; gap: 4px; overflow-x: auto; margin-bottom: 16px; padding-bottom: 4px; border-bottom: 2px solid var(--border); }
.tab-btn { padding: 8px 16px; font-size: 0.85rem; background: none; color: var(--text-secondary); border-bottom: 2px solid transparent; transition: var(--transition); white-space: nowrap; margin-bottom: -2px; }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab-btn:hover:not(.active) { color: var(--text-primary); }
.tab-panel { min-height: 200px; }
.post-pinned { border-left: 3px solid var(--warning); }
.post-flagged { border-left: 3px solid var(--danger); background: #FFF5F5; }
.user-card { cursor: pointer; transition: var(--transition); }
.user-card:hover { box-shadow: var(--shadow-lg); }
.guide-row { align-items: center; }

@media (min-width: 768px) {
  .admin-page { padding: 24px 32px; }
}
</style>

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
            <button class="btn btn-danger btn-sm" @click="deletePostById(p._id)">删除</button>
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
      <div class="file-mgmt-tabs mb-16">
        <button type="button" class="tab-btn" :class="{ active: userSubTab === 'list' }" @click="userSubTab = 'list'; loadTabData()">用户名单</button>
        <button type="button" class="tab-btn" :class="{ active: userSubTab === 'moderate' }" @click="userSubTab = 'moderate'; loadTabData()">账号处理</button>
      </div>

      <template v-if="userSubTab === 'list'">
        <div class="user-search mb-16">
          <input class="form-input" v-model="userKeyword" placeholder="搜索昵称、学号、班级、用户名…" @input="debouncedReloadUsersTab" style="max-width: 320px" />
        </div>
        <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
        <template v-else-if="usersGroupedByClass.length">
          <div v-for="g in usersGroupedByClass" :key="g.class" class="user-group mb-16">
            <h4 class="group-title mb-8">{{ g.class || '未填写班级' }}</h4>
            <div v-for="u in g.users" :key="u._id" class="card mb-8 user-card" @click="$router.push(`/admin/user/${u._id}`)">
              <div class="flex items-center gap-12">
                <div class="avatar-hit" role="button" tabindex="0" title="发私信" @click.stop="openChatWithUser(u)" @keyup.enter.stop="openChatWithUser(u)">
                  <img v-if="u.avatarUrl" class="avatar-img" :src="u.avatarUrl" alt="" />
                  <div v-else class="avatar">{{ (u.nickname || '?')[0] }}</div>
                </div>
                <div>
                  <div class="font-bold">{{ u.nickname }}</div>
                  <div class="text-xs text-muted">
                    学号：{{ u.studentId || '未绑定' }} · {{ u.role === 'admin' ? '导生' : '用户' }} · Exp: {{ u.exp || 0 }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty-state"><div class="icon">👥</div><div class="text">暂无用户</div></div>
      </template>

      <template v-else>
        <p class="text-sm text-muted mb-8">搜索并选择账号后，可执行禁言、封禁或软删除（注销）。不可处理最高管理员或本人。</p>
        <div class="user-search mb-16 flex flex-wrap gap-8 items-end">
          <input class="form-input" v-model="moderateKeyword" placeholder="搜索昵称、学号、班级、用户名…" @input="debouncedReloadUsersTab" style="max-width: 320px" />
        </div>
        <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
        <template v-else>
          <div class="card mb-16 moderate-form">
            <div class="flex flex-wrap gap-12 items-end mb-12">
              <label class="moderate-field">
                <span class="text-xs text-muted block mb-4">选择账号</span>
                <select v-model="selectedUserId" class="form-input" style="min-width: 220px; max-width: 100%">
                  <option value="">请选择</option>
                  <option v-for="u in moderateUsers" :key="u._id" :value="u._id" :disabled="u.isSuperAdmin">
                    {{ u.nickname }} · {{ u.studentId || u.username || u._id }}{{ u.isSuperAdmin ? '（超管）' : '' }}
                  </option>
                </select>
              </label>
              <label class="moderate-field">
                <span class="text-xs text-muted block mb-4">操作</span>
                <select v-model="moderateAction" class="form-input">
                  <option value="mute">禁言</option>
                  <option value="ban">封禁</option>
                  <option value="delete">删除账号</option>
                </select>
              </label>
              <label class="moderate-field">
                <span class="text-xs text-muted block mb-4">期限</span>
                <select v-model="moderateDuration" class="form-input" :disabled="moderateAction === 'delete'">
                  <option value="1d">1 天</option>
                  <option value="7d">7 天</option>
                  <option value="30d">30 天</option>
                  <option value="forever">永久</option>
                </select>
              </label>
              <button type="button" class="btn btn-danger btn-sm" :disabled="!selectedUserId" @click="submitModerate">执行</button>
            </div>
            <p v-if="moderateAction === 'delete'" class="text-xs text-muted">删除为软注销，该账号将无法登录；期限选项不适用。</p>
          </div>
          <div v-if="moderateUsers.length" class="moderate-pick-list">
            <p class="text-xs text-muted mb-8">点击一行可快速选中</p>
            <div
              v-for="u in moderateUsers"
              :key="u._id"
              class="card mb-8 user-card moderate-pick"
              :class="{ 'moderate-pick-active': selectedUserId === u._id, 'moderate-pick-disabled': u.isSuperAdmin }"
              @click="u.isSuperAdmin ? null : (selectedUserId = u._id)"
            >
              <div class="flex justify-between items-center">
                <div>
                  <span class="font-bold">{{ u.nickname }}</span>
                  <span class="text-xs text-muted ml-8">{{ u.studentId || '未绑定学号' }} · {{ u.class || '未填班级' }}</span>
                </div>
                <span v-if="u.isSuperAdmin" class="badge badge-warning">超管</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state"><div class="icon">🔍</div><div class="text">无匹配用户，请调整搜索</div></div>
        </template>
      </template>
    </div>

    <!-- File Management -->
    <div v-if="activeTab === 'fileShare'" class="tab-panel">
      <div class="file-mgmt-tabs mb-16">
        <button class="tab-btn" :class="{ active: fileSubTab === 'pending' }" @click="fileSubTab = 'pending'; loadFileTab()">待审核</button>
        <button class="tab-btn" :class="{ active: fileSubTab === 'approved' }" @click="fileSubTab = 'approved'; loadFileTab()">已发布</button>
      </div>
      <div v-if="loadingTab" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="fileSubTab === 'pending'">
        <p class="text-sm text-muted mb-8">以下文件分享待审核，通过后其他用户可见。</p>
        <template v-if="pendingFiles.length">
          <div v-for="f in pendingFiles" :key="f._id" class="card mb-8">
            <h4 class="mb-4">{{ f.title }}</h4>
            <p v-if="f.description" class="text-sm text-secondary mb-4">{{ f.description }}</p>
            <p class="text-xs text-muted mb-8">{{ f.authorName }} · {{ f.fileName || '文件' }}</p>
            <button class="btn btn-success btn-sm" @click="approveFile(f._id)">通过</button>
          </div>
        </template>
        <div v-else class="empty-state"><div class="icon">📁</div><div class="text">暂无待审核文件</div></div>
      </template>
      <template v-else>
        <p class="text-sm text-muted mb-8">已通过审核的文件，可在此删除。</p>
        <template v-if="approvedFiles.length">
          <div v-for="f in approvedFiles" :key="f._id" class="card mb-8">
            <h4 class="mb-4">{{ f.title }}</h4>
            <p v-if="f.description" class="text-sm text-secondary mb-4">{{ f.description }}</p>
            <p class="text-xs text-muted mb-8">{{ f.authorName }} · {{ f.fileName || '文件' }}</p>
            <a :href="f.fileUrl" target="_blank" rel="noopener" class="btn btn-primary btn-sm mr-8">下载</a>
            <button class="btn btn-danger btn-sm" @click="deleteFile(f._id)">删除</button>
          </div>
        </template>
        <div v-else class="empty-state"><div class="icon">📂</div><div class="text">暂无已发布文件</div></div>
      </template>
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { REVIEW_LEVEL_GUIDE, ACHIEVEMENT_CATEGORIES, POST_STATUS_LABELS } from '../../utils/config.js'
import * as api from '../../api/index.js'

const showToast = inject('showToast')
const router = useRouter()

function openChatWithUser(u) {
  if (!u?._id) return
  router.push(`/chat/${u._id}?name=${encodeURIComponent(u.nickname || '用户')}`)
}
const reviewGuide = REVIEW_LEVEL_GUIDE

const achCatMap = {}
ACHIEVEMENT_CATEGORIES.forEach(c => { achCatMap[c.key] = c.label })
function achCatLabel(key) { return achCatMap[key] || key }
function statusLabel(s) { return POST_STATUS_LABELS[s] || s }

const tabs = [
  { key: 'achievements', label: '成果审核' },
  { key: 'flagged', label: '违规帖子' },
  { key: 'allPosts', label: '全部帖子' },
  { key: 'fileShare', label: '文件管理' },
  { key: 'shop', label: '积分商店' },
  { key: 'users', label: '用户' }
]
const activeTab = ref('achievements')
const loadingTab = ref(false)

const pendingAchs = ref([])
const flaggedPosts = ref([])
const allPosts = ref([])
const pendingFiles = ref([])
const approvedFiles = ref([])
const fileSubTab = ref('pending')
const shopItems = ref([])
const users = ref([])
const userKeyword = ref('')
const userSubTab = ref('list')
const moderateKeyword = ref('')
const moderateUsers = ref([])
const selectedUserId = ref('')
const moderateAction = ref('mute')
const moderateDuration = ref('1d')
const usersGroupedByClass = computed(() => {
  const groups = {}
  for (const u of users.value) {
    const c = (u.class || '').trim() || '__none__'
    if (!groups[c]) groups[c] = { class: c === '__none__' ? '' : c, users: [] }
    groups[c].users.push(u)
  }
  return Object.values(groups).sort((a, b) => (a.class || 'zzz').localeCompare(b.class || 'zzz'))
})

let userSearchTimer = null
function debouncedReloadUsersTab() {
  clearTimeout(userSearchTimer)
  userSearchTimer = setTimeout(() => {
    if (activeTab.value === 'users') loadTabData()
  }, 300)
}

function durationLabel(d) {
  const m = { '1d': '1 天', '7d': '7 天', '30d': '30 天', forever: '永久' }
  return m[d] || d
}

async function submitModerate() {
  if (!selectedUserId.value) {
    showToast('请选择账号')
    return
  }
  const act = moderateAction.value
  const dur = moderateDuration.value
  const tip = act === 'delete'
    ? '确定软删除该账号？该用户将无法再登录。'
    : `确定对该账号执行${act === 'mute' ? '禁言' : '封禁'}（${durationLabel(dur)}）？`
  if (!window.confirm(tip)) return
  try {
    await api.adminUserModerate(selectedUserId.value, act, dur)
    showToast('已处理')
    selectedUserId.value = ''
    await loadTabData()
  } catch (e) {
    showToast(e.message || '操作失败')
  }
}

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
        await loadFileTab()
        break
      }
      case 'shop': {
        const r = await api.adminGetShopItems()
        shopItems.value = (r.items || []).map(i => ({ ...i, editStock: i.stock }))
        break
      }
      case 'users': {
        const kw = userSubTab.value === 'list'
          ? userKeyword.value.trim()
          : moderateKeyword.value.trim()
        const r = await api.adminGetUserList(kw)
        const list = r.users || []
        if (userSubTab.value === 'list') {
          users.value = list
        } else {
          moderateUsers.value = list
        }
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

async function deletePostById(id) {
  if (!window.confirm('确定删除该帖子？删除后不可恢复。')) return
  try {
    await api.deletePost(id)
    showToast('已删除')
    await loadTabData()
  } catch (e) { showToast(e.message || '删除失败') }
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

async function loadFileTab() {
  loadingTab.value = true
  try {
    if (fileSubTab.value === 'pending') {
      const r = await api.adminGetPendingFileShares()
      pendingFiles.value = r.items || []
    } else {
      const r = await api.adminGetFileShareList('approved')
      approvedFiles.value = r.items || []
    }
  } catch (e) { showToast(e.message || '加载失败') }
  finally { loadingTab.value = false }
}

async function approveFile(id) {
  try {
    await api.adminApproveFileShare(id)
    showToast('已通过')
    pendingFiles.value = pendingFiles.value.filter(f => f._id !== id)
  } catch (e) { showToast(e.message || '操作失败') }
}

async function deleteFile(id) {
  if (!confirm('确定要删除该文件吗？')) return
  try {
    await api.adminDeleteFileShare(id)
    showToast('已删除')
    approvedFiles.value = approvedFiles.value.filter(f => f._id !== id)
  } catch (e) { showToast(e.message || '操作失败') }
}

async function updateStock(item) {
  try {
    await api.adminUpdateShopStock(item.itemKey, item.editStock)
    showToast('已保存')
    item.stock = item.editStock
  } catch (e) { showToast(e.message || '操作失败') }
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
.avatar-hit { flex-shrink: 0; cursor: pointer; border-radius: 50%; }
.avatar-hit:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.avatar-img {
  width: 40px; height: 40px; border-radius: 50%; object-fit: cover;
  display: block; border: 1px solid var(--border);
}
.avatar-hit .avatar {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg); font-weight: 600; color: var(--text-secondary);
  border: 1px solid var(--border);
}
.guide-row { align-items: center; }
.file-mgmt-tabs { display: flex; gap: 8px; }
.file-mgmt-tabs .tab-btn { padding: 6px 14px; font-size: 0.85rem; }
.user-group .group-title { font-size: 0.95rem; color: var(--primary); }
.mr-8 { margin-right: 8px; }

@media (min-width: 768px) {
  .admin-page { padding: 24px 32px; }
}
</style>

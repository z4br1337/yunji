<template>
  <div class="page-container">
    <div class="page-header flex items-center gap-12 mb-16">
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.push('/settings')">‹ 返回</button>
      <h2 class="m-0">邀请与导生</h2>
    </div>

    <div class="admin-tabs mb-16">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: tab === 'invite' }"
        @click="tab = 'invite'"
      >
        邀请码
      </button>
      <button
        v-if="isSuperAdmin"
        type="button"
        class="tab-btn"
        :class="{ active: tab === 'promote' }"
        @click="tab = 'promote'; loadUsers()"
      >
        指定导生
      </button>
    </div>

    <!-- 邀请码 -->
    <div v-show="tab === 'invite'" class="card p-16">
      <p class="text-sm text-secondary mb-12">输入邀请码可将你的账号升级为导生（每个邀请码仅可使用一次）。</p>
      <div class="flex gap-8">
        <input v-model="inviteCode" class="form-input flex-1" placeholder="输入邀请码" />
        <button class="btn btn-primary btn-sm" :disabled="inviteLoading" @click="useInvite">
          {{ inviteLoading ? '…' : '使用' }}
        </button>
      </div>
    </div>

    <!-- 指定导生（最高管理员） -->
    <div v-show="tab === 'promote'" class="tab-panel">
      <div class="user-search mb-16">
        <input
          v-model="userKeyword"
          class="form-input"
          placeholder="搜索昵称、学号、班级、用户名…"
          style="max-width: 320px"
          @input="debouncedLoadUsers"
        />
      </div>
      <div v-if="loadingUsers" class="loading-spinner"><div class="spinner"></div></div>
      <template v-else-if="usersGroupedByClass.length">
        <div v-for="g in usersGroupedByClass" :key="g.class" class="user-group mb-16">
          <h4 class="group-title mb-8">{{ g.class || '未填写班级' }}</h4>
          <div
            v-for="u in g.users"
            :key="u._id"
            class="card mb-8 user-card flex items-center gap-12"
          >
            <button
              type="button"
              class="avatar-btn"
              :title="u.role === 'admin' ? '已是导生' : '点击指定为导生'"
              @click="onAvatarClick(u)"
            >
              <img v-if="u.avatarUrl" class="avatar-img" :src="u.avatarUrl" alt="" />
              <div v-else class="avatar-fallback">{{ (u.nickname || '?')[0] }}</div>
            </button>
            <div class="flex-1 min-w-0">
              <div class="font-bold">{{ u.nickname }}</div>
              <div class="text-xs text-muted">
                学号：{{ u.studentId || '未绑定' }} · {{ u.role === 'admin' ? '导生' : '用户' }} · @{{ u.username || '—' }}
              </div>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">👥</div>
        <div class="text">暂无用户</div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="confirmUser" class="modal-overlay" @click.self="confirmUser = null">
        <div class="modal-box card p-20">
          <p class="mb-16">
            是否让 <strong>{{ confirmUser.nickname }}</strong>（@{{ confirmUser.username || '—' }}）成为导生？
          </p>
          <div class="flex gap-8 justify-end">
            <button type="button" class="btn btn-ghost btn-sm" @click="confirmUser = null">取消</button>
            <button type="button" class="btn btn-primary btn-sm" :disabled="promoteLoading" @click="confirmPromote">
              {{ promoteLoading ? '处理中…' : '是' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'

const showToast = inject('showToast')
const { state, refreshProfile } = useUserStore()

const tab = ref('invite')
const isSuperAdmin = computed(() => !!state.userInfo?.isSuperAdmin)

const inviteCode = ref('')
const inviteLoading = ref(false)

const userKeyword = ref('')
const users = ref([])
const loadingUsers = ref(false)
let searchTimer = null
const confirmUser = ref(null)
const promoteLoading = ref(false)

const usersGroupedByClass = computed(() => {
  const groups = {}
  for (const u of users.value) {
    const c = (u.class || '').trim() || '__none__'
    if (!groups[c]) groups[c] = { class: c === '__none__' ? '' : c, users: [] }
    groups[c].users.push(u)
  }
  return Object.values(groups).sort((a, b) => (a.class || 'zzz').localeCompare(b.class || 'zzz'))
})

function debouncedLoadUsers() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadUsers(), 300)
}

async function loadUsers() {
  if (!isSuperAdmin.value) return
  loadingUsers.value = true
  try {
    const r = await api.adminGetUserList(userKeyword.value.trim())
    users.value = r.users || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loadingUsers.value = false
  }
}

onMounted(() => {
  if (isSuperAdmin.value && tab.value === 'promote') loadUsers()
})

async function useInvite() {
  if (!inviteCode.value.trim()) {
    showToast('请输入邀请码')
    return
  }
  inviteLoading.value = true
  try {
    await api.useInviteCode(inviteCode.value.trim())
    await refreshProfile()
    showToast('邀请码使用成功')
    inviteCode.value = ''
  } catch (e) {
    showToast(e.message || '邀请码无效')
  } finally {
    inviteLoading.value = false
  }
}

function onAvatarClick(u) {
  if (u.role === 'admin') {
    showToast('该用户已是导生')
    return
  }
  confirmUser.value = u
}

async function confirmPromote() {
  const u = confirmUser.value
  if (!u) return
  promoteLoading.value = true
  try {
    await api.adminSuperPromoteUser(u._id)
    showToast('已设为导生')
    confirmUser.value = null
    await loadUsers()
  } catch (e) {
    showToast(e.message || '操作失败')
  } finally {
    promoteLoading.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 640px;
  margin: 0 auto;
  padding: 16px;
}
.page-header h2 {
  font-size: 1.15rem;
}
.admin-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tab-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 0.9rem;
  cursor: pointer;
}
.tab-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
.group-title {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.avatar-btn {
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 50%;
  flex-shrink: 0;
}
.avatar-img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}
.avatar-fallback {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.modal-box {
  width: 100%;
  max-width: 360px;
}
.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 24px;
}
.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-muted);
}
</style>

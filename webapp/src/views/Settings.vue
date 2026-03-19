<template>
  <div class="page-container">
    <div class="page-header">
      <h2>我的</h2>
    </div>

    <!-- Profile Card -->
    <div class="profile-card card mb-16" v-if="user">
      <div class="profile-top flex items-center gap-16">
        <div class="avatar avatar-lg">
        <img v-if="user.avatarUrl" :src="user.avatarUrl" alt="" />
        <span v-else>{{ (user.nickname || '?')[0] }}</span>
      </div>
        <div class="profile-info">
          <h3>{{ user.nickname }}</h3>
          <p class="text-sm text-secondary">{{ user.class }}</p>
          <div class="badge-row flex gap-8 mt-8">
            <span v-for="b in badges" :key="b.type" class="badge" :style="{ background: b.color + '18', color: b.color }">
              {{ b.label }}
            </span>
          </div>
        </div>
      </div>
      <div class="profile-stats flex justify-between mt-16">
        <div class="stat-item text-center">
          <div class="stat-num">{{ user.exp || 0 }}</div>
          <div class="stat-label text-xs text-muted">经验值</div>
        </div>
        <div class="stat-item text-center">
          <div class="stat-num">{{ user.score || 0 }}</div>
          <div class="stat-label text-xs text-muted">积分</div>
        </div>
        <div class="stat-item text-center">
          <div class="stat-num">{{ user.postCount || 0 }}</div>
          <div class="stat-label text-xs text-muted">帖子</div>
        </div>
        <div class="stat-item text-center">
          <div class="stat-num">Lv{{ levelInfo.level }}</div>
          <div class="stat-label text-xs text-muted">{{ levelInfo.title }}</div>
        </div>
      </div>
      <!-- EXP progress -->
      <div class="exp-bar mt-8">
        <div class="exp-fill" :style="{ width: (levelInfo.progress * 100) + '%' }"></div>
      </div>
      <p class="text-xs text-muted mt-4" v-if="!levelInfo.isMax">
        距下一级还需 {{ levelInfo.expToNext - levelInfo.expInLevel }} 经验
      </p>
    </div>

    <!-- Menu -->
    <div class="card">
      <div class="menu-item" @click="$router.push('/profile-edit')">
        <span class="menu-icon">✏️</span><span>编辑资料</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/change-password')">
        <span class="menu-icon">🔐</span><span>修改密码</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/growth-book')">
        <span class="menu-icon">📖</span><span>成长手册</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/chat')">
        <span class="menu-icon">💌</span><span>私信</span><span class="arrow">›</span>
      </div>
      <div v-if="!isAdmin" class="menu-item" @click="$router.push('/emotion-help')">
        <span class="menu-icon">💙</span><span>情感倾诉专线</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="togglePointsLog">
        <span class="menu-icon">📊</span><span>积分记录</span><span class="arrow">{{ showPoints ? '⌃' : '›' }}</span>
      </div>
      <!-- Points Log -->
      <div v-if="showPoints" class="points-log">
        <div v-for="log in pointsLog" :key="log._id" class="log-item flex justify-between">
          <span class="text-sm">{{ reasonLabel(log.reason) }}</span>
          <span class="text-sm font-bold" :class="log.delta > 0 ? 'text-success' : 'text-danger'">
            {{ log.delta > 0 ? '+' : '' }}{{ log.delta }}
          </span>
        </div>
        <div v-if="!pointsLog.length" class="text-muted text-sm text-center p-16">暂无记录</div>
      </div>

      <!-- Invite Code -->
      <div class="menu-item" @click="showInvite = !showInvite">
        <span class="menu-icon">🎫</span><span>使用邀请码</span><span class="arrow">{{ showInvite ? '⌃' : '›' }}</span>
      </div>
      <div v-if="showInvite" class="invite-section p-16">
        <div class="flex gap-8">
          <input class="form-input" v-model="inviteCode" placeholder="输入邀请码" />
          <button class="btn btn-primary btn-sm" @click="useInvite">使用</button>
        </div>
      </div>

      <template v-if="isAdmin">
        <div class="divider"></div>
        <div class="menu-item" @click="$router.push('/admin')">
          <span class="menu-icon">⚙️</span><span>管理后台</span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/admin/emotion-inbox')">
          <span class="menu-icon">📬</span><span>情感倾诉信息</span><span class="arrow">›</span>
        </div>
      </template>

      <div class="divider"></div>
      <div class="menu-item menu-danger" @click="handleLogout">
        <span class="menu-icon">🚪</span><span>退出登录</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { getLevelInfo, getUserBadges } from '../utils/level.js'
import { POINTS_REASON_LABELS } from '../utils/config.js'
import * as api from '../api/index.js'

const router = useRouter()
const { state, logout, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const user = computed(() => state.userInfo)
const isAdmin = computed(() => state.isAdmin)
const levelInfo = computed(() => getLevelInfo(user.value?.exp))
const badges = computed(() => user.value ? getUserBadges(user.value) : [])

const showPoints = ref(false)
const pointsLog = ref([])
const showInvite = ref(false)
const inviteCode = ref('')

function reasonLabel(reason) { return POINTS_REASON_LABELS[reason] || reason }

async function togglePointsLog() {
  showPoints.value = !showPoints.value
  if (showPoints.value && !pointsLog.value.length) {
    try {
      const result = await api.getPointsLog()
      pointsLog.value = result.logs || []
    } catch { /* ignore */ }
  }
}

async function useInvite() {
  if (!inviteCode.value.trim()) { showToast('请输入邀请码'); return }
  try {
    await api.useInviteCode(inviteCode.value.trim())
    await refreshProfile()
    showToast('邀请码使用成功，已升级为管理员')
    showInvite.value = false
  } catch (e) {
    showToast(e.message || '邀请码无效')
  }
}

function handleLogout() {
  logout()
  router.replace('/login')
}
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.profile-top { padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.stat-num { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); }
.exp-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.exp-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--primary-light)); border-radius: 3px; transition: width 0.5s ease; }
.menu-item { display: flex; align-items: center; gap: 12px; padding: 14px 4px; cursor: pointer; transition: var(--transition); }
.menu-item:hover { background: var(--bg); }
.menu-item span:nth-child(2) { flex: 1; font-size: 0.95rem; }
.arrow { color: var(--text-muted); font-size: 1.2rem; }
.menu-danger span { color: var(--danger); }
.divider { height: 1px; background: var(--border); margin: 4px 0; }
.points-log { padding: 0 8px 8px; }
.log-item { padding: 8px 4px; border-bottom: 1px solid var(--border); }
.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
</style>

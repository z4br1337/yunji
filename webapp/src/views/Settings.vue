<template>
  <div class="page-container">
    <div class="page-header">
      <h2>我的</h2>
    </div>

    <!-- Profile Card：点击进入个人主页（统计与成长手册已迁至个人主页） -->
    <div class="profile-card card mb-16 profile-card-home-entry" v-if="user">
      <div
        class="profile-top flex items-center gap-16"
        role="button"
        tabindex="0"
        @click="goPersonalHome"
        @keyup.enter="goPersonalHome"
      >
        <div class="profile-left flex items-center gap-12">
          <div class="avatar avatar-lg">
            <img v-if="user.avatarUrl" :src="user.avatarUrl" alt="" />
            <span v-else>{{ (user.nickname || '?')[0] }}</span>
          </div>
          <div class="level-display">
            <span class="level-num">Lv{{ levelInfo.level }}</span>
            <span class="level-title">{{ levelInfo.title }}</span>
          </div>
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
      <p class="profile-home-hint text-muted">点击进入个人主页 ›</p>
    </div>

    <!-- Menu -->
    <div class="card menu-card">
      <div class="menu-item menu-item-interaction" @click="$router.push('/chat')">
        <span class="menu-interaction-icon-wrap">
          <span class="menu-interaction-icon">💌</span>
          <span v-if="interactionUnreadTotal > 0" class="menu-interaction-badge">{{ interactionBadgeText }}</span>
        </span>
        <div class="menu-interaction-text">
          <span class="menu-interaction-title">互动信息</span>
          <span class="menu-interaction-sub">评论、回复与私信汇总</span>
        </div>
        <span class="arrow menu-interaction-arrow">›</span>
      </div>
      <div class="menu-item menu-item-feature" @click="$router.push('/settings/preferences')">
        <span class="menu-icon-wrap">🔧</span>
        <div class="menu-text">
          <span class="menu-title">设置</span>
          <span class="menu-sub">个人资料 · 修改密码</span>
        </div>
        <span class="arrow">›</span>
      </div>
      <div v-if="!isAdmin" class="menu-item" @click="$router.push('/emotion-help')">
        <span class="menu-icon">💙</span><span>情感倾诉专线</span><span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/points-shop')">
        <span class="menu-icon">🛒</span><span>萤火积分兑换商店</span><span class="arrow">›</span>
      </div>

      <div class="menu-item" @click="$router.push('/settings/invite')">
        <span class="menu-icon">🎫</span><span>使用邀请码</span><span class="arrow">›</span>
      </div>

      <template v-if="isAdmin">
        <div class="divider"></div>
        <div class="menu-item" @click="$router.push('/admin/activity')">
          <span class="menu-icon">🎯</span><span>管理活动</span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/admin')">
          <span class="menu-icon">⚙️</span><span>管理后台</span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/admin/emotion-inbox')">
          <span class="menu-icon">📬</span><span>情感倾诉信息</span><span class="arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/admin/review-history')">
          <span class="menu-icon">📜</span><span>处理历史记录</span><span class="arrow">›</span>
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
import { ref, computed, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { getLevelInfo, getUserBadges } from '../utils/level.js'
const router = useRouter()
const { state, logout } = useUserStore()
const showToast = inject('showToast')
const interactionUnreadTotal = inject('interactionUnreadTotal', ref(0))
const refreshInteractionUnread = inject('refreshInteractionUnread', () => {})

const interactionBadgeText = computed(() => {
  const n = interactionUnreadTotal.value
  return n > 99 ? '99+' : String(n)
})

const user = computed(() => state.userInfo)
const isAdmin = computed(() => state.isAdmin)
const levelInfo = computed(() => getLevelInfo(user.value?.exp))
const badges = computed(() => {
  const b = user.value ? getUserBadges(user.value) : []
  return b.filter(x => x.type !== 'level')
})

function goPersonalHome() {
  router.push('/profile')
}

onMounted(async () => {
  try {
    await refreshInteractionUnread()
  } catch { /* ignore */ }
})

watch(
  () => state.isLoggedIn,
  (v) => {
    if (v) refreshInteractionUnread()
  }
)

function handleLogout() {
  logout()
  router.replace('/login')
}
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.menu-card { overflow: hidden; box-shadow: var(--shadow); border: 1px solid var(--border); }
.menu-item-interaction {
  padding: 20px 16px !important;
  gap: 16px !important;
  align-items: center !important;
  background: linear-gradient(135deg, rgba(254, 44, 85, 0.06), rgba(74, 144, 217, 0.08));
  border: 1px solid rgba(74, 144, 217, 0.22);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
  box-shadow: 0 4px 14px rgba(74, 144, 217, 0.12);
}
.menu-item-interaction:hover {
  background: linear-gradient(135deg, rgba(254, 44, 85, 0.09), rgba(74, 144, 217, 0.12));
  border-color: rgba(74, 144, 217, 0.35);
}
.menu-interaction-icon-wrap {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(145deg, #fff5f7, #e8f4fc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.65rem;
  flex-shrink: 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}
.menu-interaction-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  line-height: 20px;
  text-align: center;
  box-sizing: border-box;
}
.menu-interaction-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.menu-interaction-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}
.menu-interaction-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
}
.menu-interaction-arrow {
  font-size: 1.45rem !important;
  font-weight: 300;
  opacity: 0.75;
}
.menu-item-feature {
  background: linear-gradient(135deg, rgba(74, 144, 217, 0.06), rgba(107, 165, 231, 0.04));
  border-bottom: 1px solid var(--border);
  padding: 16px 12px !important;
}
.menu-item-feature:hover { background: linear-gradient(135deg, rgba(74, 144, 217, 0.1), rgba(107, 165, 231, 0.06)); }
.menu-icon-wrap {
  width: 44px; height: 44px; border-radius: 12px;
  background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem; flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(74, 144, 217, 0.15);
}
.menu-text { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.menu-title { font-size: 1rem; font-weight: 600; color: var(--text-primary); }
.menu-sub { font-size: 0.75rem; color: var(--text-muted); }
.profile-card-home-entry { position: relative; padding-bottom: 28px; }
.profile-top { padding-bottom: 16px; border-bottom: 1px solid var(--border); border-radius: var(--radius-sm); transition: background 0.15s ease; }
.profile-top:hover { background: var(--bg); }
.profile-top:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.profile-home-hint { position: absolute; right: 14px; bottom: 10px; margin: 0; font-size: 0.8rem; opacity: 0.88; pointer-events: none; line-height: 1.3; }
.profile-left { display: flex; align-items: center; gap: 12px; }
.level-display {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
}
.level-num {
  font-size: 1.4rem; font-weight: 700;
  color: #7EC8E3; text-shadow: 0 1px 2px rgba(126,200,227,0.4);
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.08em;
}
.level-title {
  font-size: 0.7rem; color: #7EC8E3; opacity: 0.9;
}
.menu-icon-wrap-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
}
.menu-icon-badge {
  position: absolute;
  top: -7px;
  right: -12px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: #fe2c55;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  line-height: 16px;
  text-align: center;
  box-sizing: border-box;
}
.menu-item { display: flex; align-items: center; gap: 12px; padding: 14px 4px; cursor: pointer; transition: var(--transition); }
.menu-item:hover { background: var(--bg); }
.menu-item:not(.menu-item-feature) span:nth-child(2) { flex: 1; font-size: 0.95rem; }
.arrow { color: var(--text-muted); font-size: 1.2rem; }
.menu-danger span { color: var(--danger); }
.divider { height: 1px; background: var(--border); margin: 4px 0; }
.points-log { padding: 0 8px 8px; }
.log-item { padding: 8px 4px; border-bottom: 1px solid var(--border); }
.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
</style>

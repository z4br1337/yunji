<template>
  <div class="app-root" :class="{ 'is-mobile': isMobile, 'is-desktop': !isMobile, 'is-windows': isWindows, 'is-android': isAndroid, 'is-ios': isIOS }">
    <!-- Desktop: sidebar layout -->
    <aside v-if="!isMobile && isLoggedIn" class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">✨</span>
        <span class="brand-text">云迹</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/feed" class="nav-item" active-class="active">
          <span class="nav-icon">🏠</span><span class="nav-label">广场</span>
        </router-link>
        <router-link to="/publish" class="nav-item" active-class="active">
          <span class="nav-icon">✏️</span><span class="nav-label">发布内容</span>
        </router-link>
        <router-link to="/points-shop" class="nav-item" active-class="active">
          <span class="nav-icon">🛒</span><span class="nav-label">萤火商店</span>
        </router-link>
        <router-link to="/ai-chat" class="nav-item" active-class="active">
          <span class="nav-icon">🤖</span><span class="nav-label">AI问答</span>
        </router-link>
        <router-link to="/growth-book" class="nav-item" active-class="active">
          <span class="nav-icon">🌟</span><span class="nav-label">闪光时刻</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="nav-icon">👤</span><span class="nav-label">我的</span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-item" active-class="active">
          <span class="nav-icon">⚙️</span><span class="nav-label">管理后台</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-brief" v-if="userInfo">
          <div class="avatar avatar-sm">
          <img v-if="userInfo.avatarUrl" :src="userInfo.avatarUrl" alt="" />
          <span v-else>{{ (userInfo.nickname || '?')[0] }}</span>
        </div>
          <span class="user-name">{{ userInfo.nickname }}</span>
        </div>
      </div>
    </aside>

    <!-- Main content area -->
    <main class="main-content" :class="{ 'with-sidebar': !isMobile && isLoggedIn }">
      <router-view v-slot="{ Component }">
        <component :is="Component" :key="$route.fullPath" />
      </router-view>
    </main>

    <!-- Mobile: bottom tab bar -->
    <nav v-if="isMobile && isLoggedIn && showTabBar" class="tabbar">
      <router-link to="/feed" class="tab-item" active-class="active">
        <span class="tab-icon">🏠</span><span class="tab-label">广场</span>
      </router-link>
      <router-link to="/publish" class="tab-item" active-class="active">
        <span class="tab-icon">✏️</span><span class="tab-label">发布内容</span>
      </router-link>
      <router-link to="/points-shop" class="tab-item" active-class="active">
        <span class="tab-icon">🛒</span><span class="tab-label">萤火商店</span>
      </router-link>
      <router-link to="/ai-chat" class="tab-item" active-class="active">
        <span class="tab-icon">🤖</span><span class="tab-label">AI问答</span>
      </router-link>
      <router-link to="/growth-book" class="tab-item" active-class="active">
        <span class="tab-icon">🌟</span><span class="tab-label">闪光时刻</span>
      </router-link>
      <router-link to="/settings" class="tab-item" active-class="active">
        <span class="tab-icon">👤</span><span class="tab-label">我的</span>
      </router-link>
    </nav>

    <!-- Toast -->
    <div class="toast-container" v-if="toasts.length">
      <div class="toast" v-for="t in toasts" :key="t.id">{{ t.msg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useDevice } from './utils/device.js'
import { useUserStore } from './stores/user.js'
import * as api from './api/index.js'

const { isMobile, isWindows, isAndroid, isIOS } = useDevice()
const { state, restoreSession, refreshProfile } = useUserStore()
const route = useRoute()

const isLoggedIn = computed(() => state.isLoggedIn)
const isAdmin = computed(() => state.isAdmin)
const userInfo = computed(() => state.userInfo)

const interactionUnreadTotal = ref(0)
const interactionBadgeText = computed(() => {
  const n = interactionUnreadTotal.value
  return n > 99 ? '99+' : String(n)
})

async function refreshInteractionUnread() {
  if (!state.isLoggedIn || !localStorage.getItem('token')) {
    interactionUnreadTotal.value = 0
    return
  }
  try {
    const r = await api.getInteractionUnreadSummary()
    interactionUnreadTotal.value = Number(r.total) || 0
  } catch {
    interactionUnreadTotal.value = 0
  }
}

provide('refreshInteractionUnread', refreshInteractionUnread)
provide('interactionUnreadTotal', interactionUnreadTotal)

watch(isLoggedIn, async (v) => {
  if (v && localStorage.getItem('token')) {
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  } else {
    interactionUnreadTotal.value = 0
  }
})

const hideTabBarRoutes = ['/login', '/register', '/bind-student', '/profile-edit', '/settings/preferences', '/achievement/create', '/emotion-help']
const showTabBar = computed(() => {
  return !hideTabBarRoutes.some(r => route.path.startsWith(r))
    && !route.path.startsWith('/chat/')
    && !route.path.startsWith('/admin')
})

const toasts = ref([])
let toastId = 0
function showToast(msg, duration = 2000) {
  const id = ++toastId
  toasts.value.push({ id, msg })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, duration)
}

provide('showToast', showToast)
provide('isMobile', isMobile)
provide('isWindows', isWindows)
provide('isAndroid', isAndroid)
provide('isIOS', isIOS)

onMounted(async () => {
  restoreSession()
  if (state.isLoggedIn && localStorage.getItem('token')) {
    try {
      await refreshProfile()
    } catch { /* 网络异常时保留本地缓存 */ }
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  }
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', onVisibilityChange)
})

let visibilityDebounce = null
function onVisibilityChange() {
  if (document.visibilityState !== 'visible') return
  if (!state.isLoggedIn || !localStorage.getItem('token')) return
  clearTimeout(visibilityDebounce)
  visibilityDebounce = setTimeout(async () => {
    try {
      await refreshProfile()
    } catch { /* 静默失败，保留本地缓存 */ }
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  }, 300)
}
</script>

<style scoped>
/* ========== Sidebar (desktop) ========== */
.sidebar {
  position: fixed; left: 0; top: 0; bottom: 0;
  width: var(--sidebar-w); background: var(--bg-sidebar);
  display: flex; flex-direction: column; z-index: 100;
  box-shadow: 2px 0 16px rgba(0,0,0,0.1);
}
.is-windows .sidebar { box-shadow: 1px 0 8px rgba(0,0,0,0.06); }
.sidebar-brand {
  padding: 24px 20px; display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.brand-icon { font-size: 1.6rem; }
.brand-text { color: #fff; font-size: 1.3rem; font-weight: 700; letter-spacing: 2px; }
.sidebar-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 24px; color: rgba(255,255,255,0.65);
  font-size: 0.95rem; transition: var(--transition); text-decoration: none;
  border-left: 3px solid transparent;
}
.nav-item:hover { color: #fff; background: rgba(255,255,255,0.06); }
.nav-item.active { color: #fff; background: rgba(74,144,217,0.2); border-left-color: var(--primary); }
.nav-icon-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
}
.nav-icon { font-size: 1.15rem; width: 24px; text-align: center; }
.icon-badge {
  position: absolute;
  top: -6px;
  right: -10px;
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
.tab-badge {
  top: -4px;
  right: -6px;
}
.sidebar-footer { padding: 16px 20px; border-top: 1px solid rgba(255,255,255,0.08); }
.user-brief { display: flex; align-items: center; gap: 10px; color: rgba(255,255,255,0.8); font-size: 0.85rem; }

/* ========== Main content ========== */
.main-content { min-height: 100vh; transition: var(--transition); }
.main-content.with-sidebar { margin-left: var(--sidebar-w); }

/* ========== Tabbar (mobile) ========== */
.tabbar {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: var(--tabbar-h); background: #fff;
  display: flex; align-items: center; justify-content: space-around;
  box-shadow: 0 -2px 12px rgba(0,0,0,0.06); z-index: 100;
  border-top: 1px solid var(--border);
}
.tab-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  font-size: 0.62rem; color: var(--text-muted); text-decoration: none;
  transition: var(--transition); padding: 4px 0;
  min-width: 0; flex: 1;
}
.tab-item.active { color: var(--primary); }
.tab-icon-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.tab-icon { font-size: 1.2rem; }
.tab-label { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ========== Mobile padding ========== */
.is-mobile .main-content { padding-bottom: calc(var(--tabbar-h) + 8px); }

/* ========== Transition ========== */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

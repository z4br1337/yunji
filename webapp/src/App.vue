<template>
  <div class="app-root" :class="{ 'is-mobile': isMobile, 'is-desktop': !isMobile, 'is-windows': isWindows, 'is-android': isAndroid, 'is-ios': isIOS }">
    <aside v-if="!isMobile && isLoggedIn" class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">云</div>
        <div>
          <div class="brand-text">云迹</div>
          <div class="brand-subtext">哲法er交流学习平台</div>
        </div>
      </div>

      <div class="sidebar-search">
        <button class="sidebar-search-btn" type="button" @click="$router.push('/search')">
          <span>搜索你感兴趣的内容</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/feed" class="nav-item" active-class="active">
          <span class="nav-icon">首页</span><span class="nav-label">广场</span>
        </router-link>
        <router-link to="/publish" class="nav-item" active-class="active">
          <span class="nav-icon">发布</span><span class="nav-label">发布内容</span>
        </router-link>
        <router-link to="/points-shop" class="nav-item" active-class="active">
          <span class="nav-icon">商店</span><span class="nav-label">萤火商店</span>
        </router-link>
        <router-link to="/ai-chat" class="nav-item" active-class="active">
          <span class="nav-icon">问答</span><span class="nav-label">AI问答</span>
        </router-link>
        <router-link to="/growth-book" class="nav-item" active-class="active">
          <span class="nav-icon">成长</span><span class="nav-label">闪光时刻</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="nav-icon">我的</span><span class="nav-label">个人中心</span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-item" active-class="active">
          <span class="nav-icon">管理</span><span class="nav-label">管理后台</span>
        </router-link>
      </nav>

      <div class="sidebar-footer" v-if="userInfo">
        <div class="user-brief">
          <div class="avatar avatar-sm">
            <img v-if="userInfo.avatarUrl" :src="userInfo.avatarUrl" alt="" />
            <span v-else>{{ (userInfo.nickname || '?')[0] }}</span>
          </div>
          <div>
            <div class="user-name">{{ userInfo.nickname }}</div>
            <div class="user-meta">{{ userInfo.class || '未填写班级' }}</div>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content" :class="{ 'with-sidebar': !isMobile && isLoggedIn }">
      <router-view v-slot="{ Component }">
        <component :is="Component" :key="$route.fullPath" />
      </router-view>
    </main>

    <nav v-if="isMobile && isLoggedIn && showTabBar" class="tabbar">
      <router-link to="/feed" class="tab-item" active-class="active"><span class="tab-icon">首页</span><span class="tab-label">广场</span></router-link>
      <router-link to="/publish" class="tab-item" active-class="active"><span class="tab-icon">发布</span><span class="tab-label">发布内容</span></router-link>
      <router-link to="/points-shop" class="tab-item" active-class="active"><span class="tab-icon">商店</span><span class="tab-label">萤火商店</span></router-link>
      <router-link to="/ai-chat" class="tab-item" active-class="active"><span class="tab-icon">问答</span><span class="tab-label">AI问答</span></router-link>
      <router-link to="/growth-book" class="tab-item" active-class="active"><span class="tab-icon">成长</span><span class="tab-label">闪光时刻</span></router-link>
      <router-link to="/settings" class="tab-item" active-class="active"><span class="tab-icon">我的</span><span class="tab-label">个人中心</span></router-link>
    </nav>

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
const { state, restoreSession, refreshProfile, syncSessionFromServer } = useUserStore()
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
      await syncSessionFromServer()
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
      await syncSessionFromServer()
    } catch { /* 静默失败，保留本地缓存 */ }
    try {
      await refreshInteractionUnread()
    } catch { /* ignore */ }
  }, 300)
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-w);
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(18px);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 100;
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}
.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary);
  color: #fff;
  font-weight: 700;
}
.brand-text { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.brand-subtext { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }
.sidebar-search { padding: 16px 16px 8px; }
.sidebar-search-btn {
  width: 100%;
  height: 40px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg-muted);
  color: var(--text-muted);
  text-align: left;
  padding: 0 16px;
}
.sidebar-nav {
  flex: 1;
  padding: 8px 12px;
  overflow-y: auto;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  margin: 4px 0;
  border-radius: 12px;
  color: var(--text-primary);
  text-decoration: none;
  transition: var(--transition);
}
.nav-item:hover { background: var(--bg-muted); }
.nav-item.active { background: rgba(255,130,0,0.12); color: var(--primary); font-weight: 600; }
.nav-icon { width: 40px; height: 28px; display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; background: var(--bg-muted); font-size: 0.8rem; color: var(--text-secondary); }
.nav-item.active .nav-icon { background: rgba(255,130,0,0.16); color: var(--primary); }
.nav-label { font-size: 0.95rem; }
.sidebar-footer { padding: 16px; border-top: 1px solid var(--border); }
.user-brief { display: flex; align-items: center; gap: 10px; }
.user-name { font-size: 0.92rem; font-weight: 600; color: var(--text-primary); }
.user-meta { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }
.main-content { min-height: 100vh; transition: var(--transition); }
.main-content.with-sidebar { margin-left: var(--sidebar-w); }
.tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: var(--tabbar-h);
  background: rgba(255,255,255,0.98);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 100;
}
.tab-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-decoration: none;
  color: var(--text-muted);
  font-size: 0.7rem;
}
.tab-item.active { color: var(--primary); font-weight: 600; }
.tab-icon { font-size: 0.78rem; line-height: 1; }
.tab-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.is-mobile .main-content { padding-bottom: calc(var(--tabbar-h) + 8px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

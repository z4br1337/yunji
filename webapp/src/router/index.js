import { createRouter, createWebHistory } from 'vue-router'

const routeLoaders = {
  Login: () => import('../views/Login.vue'),
  Register: () => import('../views/Register.vue'),
  BindStudent: () => import('../views/BindStudent.vue'),
  ProfileEdit: () => import('../views/ProfileEdit.vue'),
  ChangePassword: () => import('../views/ChangePassword.vue'),
  Feed: () => import('../views/Feed.vue'),
  SearchPage: () => import('../views/SearchPage.vue'),
  ActivityList: () => import('../views/ActivityListPage.vue'),
  RecentActivity: () => import('../views/RecentActivityPage.vue'),
  PublishContent: () => import('../views/PublishContent.vue'),
  PostCreate: () => import('../views/PostCreate.vue'),
  PostDetail: () => import('../views/PostDetail.vue'),
  AchievementCreate: () => import('../views/AchievementCreate.vue'),
  FileShare: () => import('../views/FileShare.vue'),
  AiChat: () => import('../views/AiChat.vue'),
  Settings: () => import('../views/Settings.vue'),
  PersonalHome: () => import('../views/PersonalHome.vue'),
  SettingsPreferences: () => import('../views/SettingsPreferences.vue'),
  MyPosts: () => import('../views/MyPosts.vue'),
  MyFileShares: () => import('../views/MyFileShares.vue'),
  PointsShop: () => import('../views/PointsShop.vue'),
  GrowthBook: () => import('../views/GrowthBookPage.vue'),
  ChatList: () => import('../views/ChatList.vue'),
  ChatDetail: () => import('../views/ChatDetail.vue'),
  EmotionHelp: () => import('../views/EmotionHelp.vue'),
  EmotionPostDetail: () => import('../views/EmotionPostDetail.vue'),
  AdminDashboard: () => import('../views/admin/Dashboard.vue'),
  AdminActivityCreate: () => import('../views/AdminActivityCreate.vue'),
  EmotionInbox: () => import('../views/admin/EmotionInbox.vue'),
  EmotionInboxDetail: () => import('../views/admin/EmotionInboxDetail.vue'),
  AdminUserProfile: () => import('../views/admin/UserProfile.vue'),
  AdminReviewHistory: () => import('../views/admin/AdminReviewHistory.vue')
}

const routes = [
  { path: '/', redirect: '/feed' },
  { path: '/login', name: 'Login', component: routeLoaders.Login, meta: { public: true } },
  { path: '/register', name: 'Register', component: routeLoaders.Register, meta: { public: true } },
  { path: '/bind-student', name: 'BindStudent', component: routeLoaders.BindStudent },
  { path: '/profile-edit', name: 'ProfileEdit', component: routeLoaders.ProfileEdit },
  { path: '/change-password', name: 'ChangePassword', component: routeLoaders.ChangePassword },
  { path: '/feed', name: 'Feed', component: routeLoaders.Feed },
  { path: '/search', name: 'SearchPage', component: routeLoaders.SearchPage },
  { path: '/activities', name: 'ActivityList', component: routeLoaders.ActivityList },
  { path: '/activity/:campaignId', name: 'RecentActivity', component: routeLoaders.RecentActivity },
  { path: '/activity', redirect: '/activities' },
  { path: '/publish', name: 'PublishContent', component: routeLoaders.PublishContent },
  { path: '/post/create', name: 'PostCreate', component: routeLoaders.PostCreate },
  { path: '/post/:id', name: 'PostDetail', component: routeLoaders.PostDetail },
  { path: '/achievements', redirect: '/growth-book' },
  { path: '/achievement/create', name: 'AchievementCreate', component: routeLoaders.AchievementCreate },
  { path: '/file-share', name: 'FileShare', component: routeLoaders.FileShare },
  { path: '/ai-chat', name: 'AiChat', component: routeLoaders.AiChat },
  { path: '/settings', name: 'Settings', component: routeLoaders.Settings },
  { path: '/profile/:userId?', name: 'PersonalHome', component: routeLoaders.PersonalHome },
  { path: '/settings/preferences', name: 'SettingsPreferences', component: routeLoaders.SettingsPreferences },
  { path: '/my-posts', name: 'MyPosts', component: routeLoaders.MyPosts },
  { path: '/my-files', name: 'MyFileShares', component: routeLoaders.MyFileShares },
  { path: '/points-shop', name: 'PointsShop', component: routeLoaders.PointsShop },
  { path: '/growth-book', name: 'GrowthBook', component: routeLoaders.GrowthBook },
  { path: '/chat', name: 'ChatList', component: routeLoaders.ChatList },
  { path: '/chat/:peerId', name: 'ChatDetail', component: routeLoaders.ChatDetail },
  { path: '/emotion-help', name: 'EmotionHelp', component: routeLoaders.EmotionHelp },
  { path: '/emotion-help/:id', name: 'EmotionPostDetail', component: routeLoaders.EmotionPostDetail },
  { path: '/admin', name: 'AdminDashboard', component: routeLoaders.AdminDashboard, meta: { admin: true } },
  { path: '/admin/activity', name: 'AdminActivityCreate', component: routeLoaders.AdminActivityCreate, meta: { admin: true } },
  { path: '/admin/emotion-inbox', name: 'EmotionInbox', component: routeLoaders.EmotionInbox, meta: { admin: true } },
  { path: '/admin/emotion-inbox/:postId', name: 'EmotionInboxDetail', component: routeLoaders.EmotionInboxDetail, meta: { admin: true } },
  { path: '/admin/user/:userId', name: 'AdminUserProfile', component: routeLoaders.AdminUserProfile, meta: { admin: true } },
  { path: '/admin/review-history', name: 'AdminReviewHistory', component: routeLoaders.AdminReviewHistory, meta: { admin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function userHasStudentId(user) {
  return !!(user && user.studentId && String(user.studentId).trim())
}

router.beforeEach((to, from, next) => {
  if (to.meta.public) return next()
  const token = localStorage.getItem('token')
  const stored = localStorage.getItem('userInfo')
  if (!token || !stored) {
    if (stored) {
      localStorage.removeItem('userInfo')
    }
    return next('/login')
  }
  let user
  try {
    user = JSON.parse(stored)
  } catch {
    return next('/login')
  }
  if (!userHasStudentId(user)) {
    if (to.path === '/bind-student') return next()
    return next('/bind-student')
  }
  const profileOk = !!user.profileCompleted
  const allowIncomplete =
    to.path === '/profile-edit'
    || to.path === '/change-password'
    || to.path === '/settings/preferences'
  if (!profileOk && !allowIncomplete) {
    return next('/profile-edit')
  }
  if (to.meta.admin) {
    if (user.role !== 'admin') return next('/feed')
    if (!profileOk) return next('/profile-edit')
  }
  next()
})

const prefetchQueue = new Set()
function prefetchRoute(name) {
  const loader = routeLoaders[name]
  if (!loader || prefetchQueue.has(name)) return
  prefetchQueue.add(name)
  const run = () => loader().catch(() => {}).finally(() => prefetchQueue.delete(name))
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    window.requestIdleCallback(run, { timeout: 1500 })
  } else if (typeof window !== 'undefined') {
    window.setTimeout(run, 800)
  }
}

if (typeof window !== 'undefined') {
  const warmRoutes = ['Feed', 'PublishContent', 'PostCreate', 'SearchPage', 'AiChat', 'Settings', 'GrowthBook', 'ActivityList']
  warmRoutes.forEach(prefetchRoute)
}


export default router

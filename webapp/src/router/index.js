import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/feed' },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { public: true } },
  { path: '/profile-edit', name: 'ProfileEdit', component: () => import('../views/ProfileEdit.vue') },
  { path: '/change-password', name: 'ChangePassword', component: () => import('../views/ChangePassword.vue') },
  { path: '/feed', name: 'Feed', component: () => import('../views/Feed.vue') },
  { path: '/publish', name: 'PublishContent', component: () => import('../views/PublishContent.vue') },
  { path: '/post/create', name: 'PostCreate', component: () => import('../views/PostCreate.vue') },
  { path: '/post/:id', name: 'PostDetail', component: () => import('../views/PostDetail.vue') },
  { path: '/achievements', name: 'Achievements', component: () => import('../views/Achievements.vue') },
  { path: '/achievement/create', name: 'AchievementCreate', component: () => import('../views/AchievementCreate.vue') },
  { path: '/file-share', name: 'FileShare', component: () => import('../views/FileShare.vue') },
  { path: '/ai-chat', name: 'AiChat', component: () => import('../views/AiChat.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
  { path: '/my-posts', name: 'MyPosts', component: () => import('../views/MyPosts.vue') },
  { path: '/my-files', name: 'MyFileShares', component: () => import('../views/MyFileShares.vue') },
  { path: '/points-shop', name: 'PointsShop', component: () => import('../views/PointsShop.vue') },
  { path: '/growth-book', name: 'GrowthBook', component: () => import('../views/GrowthBook.vue') },
  { path: '/chat', name: 'ChatList', component: () => import('../views/ChatList.vue') },
  { path: '/chat/:peerId', name: 'ChatDetail', component: () => import('../views/ChatDetail.vue') },
  { path: '/emotion-help', name: 'EmotionHelp', component: () => import('../views/EmotionHelp.vue') },
  { path: '/emotion-help/:id', name: 'EmotionPostDetail', component: () => import('../views/EmotionPostDetail.vue') },
  { path: '/admin', name: 'AdminDashboard', component: () => import('../views/admin/Dashboard.vue'), meta: { admin: true } },
  { path: '/admin/emotion-inbox', name: 'EmotionInbox', component: () => import('../views/admin/EmotionInbox.vue'), meta: { admin: true } },
  { path: '/admin/emotion-inbox/:postId', name: 'EmotionInboxDetail', component: () => import('../views/admin/EmotionInboxDetail.vue'), meta: { admin: true } },
  { path: '/admin/user/:userId', name: 'AdminUserProfile', component: () => import('../views/admin/UserProfile.vue'), meta: { admin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

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
  if (to.meta.admin) {
    try {
      const user = JSON.parse(stored)
      if (user.role !== 'admin') return next('/feed')
    } catch { return next('/login') }
  }
  next()
})

export default router

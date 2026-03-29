import { LOCAL_TEST_MODE, API_BASE_URL } from '../utils/config.js'
import * as mock from './mock.js'

const REQUEST_TIMEOUT_MS = 12000
const requestCache = new Map()

function buildCacheKey(path, data, method) {
  return `${method}:${path}:${JSON.stringify(data || {})}`
}

function clearExpiredCache() {
  const now = Date.now()
  for (const [key, item] of requestCache.entries()) {
    if (item.expireAt <= now) requestCache.delete(key)
  }
}

async function request(path, data = {}, method = 'POST', options = {}) {
  if (LOCAL_TEST_MODE) return null
  clearExpiredCache()

  const cacheable = Boolean(options.cacheable)
  const cacheTTL = options.cacheTTL || 5000
  const cacheKey = cacheable ? buildCacheKey(path, data, method) : ''
  if (cacheable && requestCache.has(cacheKey)) {
    return requestCache.get(cacheKey).data
  }

  const token = localStorage.getItem('token') || ''
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  let res
  try {
    res = await fetch(API_BASE_URL + path, {
      method,
      headers: { 'Content-Type': 'application/json', 'Authorization': token ? `Bearer ${token}` : '' },
      body: method !== 'GET' ? JSON.stringify(data) : undefined,
      signal: controller.signal
    })
  } catch (e) {
    if (e?.name === 'AbortError') throw new Error('请求超时，请稍后重试')
    throw e
  } finally {
    clearTimeout(timeoutId)
  }
  const contentType = res.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new Error(`服务器响应异常 (${res.status})`)
  }
  const json = await res.json()
  if (json.code !== 0) throw new Error(json.message || '请求失败')
  if (cacheable) {
    requestCache.set(cacheKey, {
      data: json.data,
      expireAt: Date.now() + cacheTTL
    })
  }
  return json.data
}

export async function register(nickname, username, password) {
  if (LOCAL_TEST_MODE) {
    const data = await mock.mockRegister(nickname, username, password)
    if (data.token) localStorage.setItem('token', data.token)
    return data
  }
  const data = await request('/user/register', { nickname, username, password })
  if (data.token) localStorage.setItem('token', data.token)
  return data
}

export function clearCache() {
  requestCache.clear()
}

export async function login(username, password) {
  if (LOCAL_TEST_MODE) {
    const r = await mock.mockLogin(username, password)
    if (r && r.__pickAccount) return r
    if (r && r._id) localStorage.setItem('token', r._id)
    requestCache.clear()
    return r
  }
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  let res
  try {
    res = await fetch(API_BASE_URL + '/user/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      signal: controller.signal,
    })
  } finally {
    clearTimeout(timeoutId)
  }
  const json = await res.json()
  if (json.code === 'PICK_ACCOUNT') {
    return {
      __pickAccount: true,
      accounts: (json.data && json.data.accounts) || [],
      message: json.message || '',
    }
  }
  if (json.code !== 0) throw new Error(json.message || '登录失败')
  const data = json.data
  if (data.token) localStorage.setItem('token', data.token)
  requestCache.clear()
  return data.user || data
}

export async function getProfile() {
  if (LOCAL_TEST_MODE) return mock.mockGetProfile()
  return request('/user/profile')
}

export async function updateProfile(data) {
  if (LOCAL_TEST_MODE) return mock.mockUpdateProfile(data)
  const result = await request('/user/profile', data)
  clearCache()
  return result
}

export const AVATAR_MAX_SIZE_BYTES = 700 * 1024  // 700KB

export async function changePassword(oldPassword, newPassword) {
  if (LOCAL_TEST_MODE) return { changed: true }
  return request('/user/change-password', { oldPassword, newPassword })
}

export async function bindStudentId(studentId) {
  if (LOCAL_TEST_MODE) return mock.mockBindStudentId(studentId)
  const data = await request('/user/bind-student-id', { studentId })
  clearCache()
  return data
}

export async function useInviteCode(code) {
  if (LOCAL_TEST_MODE) return mock.mockUseInviteCode(code)
  const result = await request('/user/invite', { code })
  clearCache()
  return result
}

export async function getPointsLog() {
  if (LOCAL_TEST_MODE) return mock.mockGetPointsLog()
  return request('/user/points-log')
}

export async function getPosts(params = {}) {
  if (LOCAL_TEST_MODE) return mock.mockGetPosts(params)
  const { page, pageSize, ...filterFields } = params
  const hasKeyword = !!(filterFields.keyword && String(filterFields.keyword).trim())
  return request(
    '/post/list',
    { filter: filterFields, page: page || 1, pageSize: pageSize || 12 },
    'POST',
    { cacheable: !hasKeyword, cacheTTL: 8000 }
  )
}

export async function getPostDetail(postId) {
  if (LOCAL_TEST_MODE) return mock.mockGetPostDetail(postId)
  return request('/post/detail', { postId })
}

export async function createPost(data) {
  if (LOCAL_TEST_MODE) return mock.mockCreatePost(data)
  const result = await request('/post/create', data)
  clearCache()
  return result
}

export async function deletePost(postId) {
  if (LOCAL_TEST_MODE) return mock.mockDeletePost(postId)
  const result = await request('/post/delete', { postId })
  clearCache()
  return result
}

export async function getComments(postId) {
  if (LOCAL_TEST_MODE) return mock.mockGetComments(postId)
  return request('/comment/list', { postId })
}

export async function addComment(postId, content, opts = {}) {
  if (LOCAL_TEST_MODE) return mock.mockAddComment(postId, content, opts)
  const body = { postId, content }
  if (opts.parentCommentId) body.parentCommentId = String(opts.parentCommentId)
  const result = await request('/comment/add', body)
  clearCache()
  return result
}

export async function deleteComment(commentId) {
  if (LOCAL_TEST_MODE) return mock.mockDeleteComment(commentId)
  const result = await request('/comment/delete', { commentId })
  clearCache()
  return result
}

export async function getAchievements(params = {}) {
  if (LOCAL_TEST_MODE) return mock.mockGetAchievements(params)
  return request('/achievement/list', params)
}

export async function createAchievement(data) {
  if (LOCAL_TEST_MODE) return mock.mockCreateAchievement(data)
  const result = await request('/achievement/create', data)
  clearCache()
  return result
}

export async function getGrowthBook(userId) {
  if (LOCAL_TEST_MODE) return mock.mockGetGrowthBook(userId)
  return request('/growth-book/get', { userId })
}

export async function setGrowthBookPublic(isPublic) {
  if (LOCAL_TEST_MODE) return mock.mockSetGrowthBookPublic(isPublic)
  const result = await request('/growth-book/set-public', { isPublic })
  clearCache()
  return result
}

export async function sendMessage(toId, content) {
  if (LOCAL_TEST_MODE) return mock.mockSendMessage(toId, content)
  const result = await request('/message/send', { toId, content })
  clearCache()
  return result
}

export async function getConversations() {
  if (LOCAL_TEST_MODE) return mock.mockGetConversations()
  return request('/message/conversations')
}

export async function getChatHistory(peerId) {
  if (LOCAL_TEST_MODE) return mock.mockGetChatHistory(peerId)
  return request('/message/history', { peerId })
}

export async function getInteractionUnreadSummary() {
  if (LOCAL_TEST_MODE) return mock.mockInteractionUnreadSummary()
  return request('/interaction/unread-summary')
}

export async function markInteractionSeen(scope = 'all') {
  if (LOCAL_TEST_MODE) return mock.mockInteractionMarkSeen(scope)
  const result = await request('/interaction/mark-seen', { scope })
  clearCache()
  return result
}

export async function getRepliesToMe() {
  if (LOCAL_TEST_MODE) return mock.mockRepliesToMe()
  return request('/interaction/replies-to-me')
}

export async function getCommentsOnMyPosts() {
  if (LOCAL_TEST_MODE) return mock.mockCommentsOnMyPosts()
  return request('/interaction/comments-on-my-posts')
}

export async function uploadImage(file) {
  if (LOCAL_TEST_MODE) return mock.mockUploadImage(file)
  const optimizedFile = await optimizeImageBeforeUpload(file)
  const formData = new FormData()
  formData.append('file', optimizedFile)
  const token = localStorage.getItem('token') || ''
  const res = await fetch(API_BASE_URL + '/upload/image', {
    method: 'POST',
    headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    body: formData
  })
  const json = await res.json()
  if (json.code !== 0) throw new Error(json.message || '上传失败')
  return json.data
}

export async function uploadFile(file) {
  if (LOCAL_TEST_MODE) return { url: '/media/uploads/test.pdf', fileName: file.name }
  const formData = new FormData()
  formData.append('file', file)
  const token = localStorage.getItem('token') || ''
  const res = await fetch(API_BASE_URL + '/upload/file', {
    method: 'POST',
    headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    body: formData
  })
  const json = await res.json()
  if (json.code !== 0) throw new Error(json.message || '上传失败')
  return json.data
}

export async function createFileShare(data) {
  if (LOCAL_TEST_MODE) return { id: 'mock_fs_001' }
  const result = await request('/file-share/create', data)
  clearCache()
  return result
}

export async function getFileShareList(params = {}) {
  if (LOCAL_TEST_MODE) return { items: [], total: 0, hasMore: false }
  return request('/file-share/list', params)
}

export async function getShopItems() {
  if (LOCAL_TEST_MODE) return { items: [] }
  return request('/shop/items')
}

export async function shopExchange(itemKey) {
  if (LOCAL_TEST_MODE) return { score: 0 }
  const result = await request('/shop/exchange', { itemKey })
  clearCache()
  return result
}

export async function getMyExchanges() {
  if (LOCAL_TEST_MODE) return { records: [] }
  return request('/shop/my-exchanges')
}

export async function adminGetPendingFileShares() {
  if (LOCAL_TEST_MODE) return { items: [] }
  return request('/admin/file-share/pending')
}

export async function adminGetFileShareList(status) {
  if (LOCAL_TEST_MODE) return { items: [] }
  return request('/admin/file-share/list', { status })
}

export async function adminApproveFileShare(fileShareId) {
  if (LOCAL_TEST_MODE) return {}
  const result = await request('/admin/file-share/approve', { fileShareId })
  clearCache()
  return result
}

export async function adminDeleteFileShare(fileShareId) {
  if (LOCAL_TEST_MODE) return {}
  const result = await request('/admin/file-share/delete', { fileShareId })
  clearCache()
  return result
}

export async function adminGetShopItems() {
  if (LOCAL_TEST_MODE) return { items: [] }
  return request('/admin/shop/items')
}

export async function adminUpdateShopStock(itemKey, stock) {
  if (LOCAL_TEST_MODE) return {}
  const result = await request('/admin/shop/update-stock', { itemKey, stock })
  clearCache()
  return result
}

async function optimizeImageBeforeUpload(file) {
  // 非图片或小图直接上传，避免额外 CPU 开销
  if (!file || !file.type?.startsWith('image/') || file.size < 300 * 1024) return file
  if (typeof createImageBitmap !== 'function') return file

  let imageBitmap
  try {
    imageBitmap = await createImageBitmap(file)
  } catch {
    return file
  }
  const maxEdge = 1600
  const scale = Math.min(1, maxEdge / Math.max(imageBitmap.width, imageBitmap.height))
  const targetWidth = Math.max(1, Math.round(imageBitmap.width * scale))
  const targetHeight = Math.max(1, Math.round(imageBitmap.height * scale))

  const canvas = document.createElement('canvas')
  canvas.width = targetWidth
  canvas.height = targetHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return file
  ctx.drawImage(imageBitmap, 0, 0, targetWidth, targetHeight)

  const blob = await new Promise((resolve) => {
    canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.8)
  })
  if (!blob) return file

  const optimized = new File([blob], `${Date.now()}-${file.name.replace(/\.[^.]+$/, '')}.jpg`, { type: 'image/jpeg' })
  imageBitmap.close()
  return optimized.size < file.size ? optimized : file
}

// ========== 管理员 API ==========

export async function adminGetReports() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetReports()
  return request('/admin/reports')
}

export async function adminOverridePost(postId, action) {
  if (LOCAL_TEST_MODE) return mock.mockAdminOverridePost(postId, action)
  return request('/admin/post/override', { postId, newStatus: action })
}

export async function adminPinPost(postId) {
  if (LOCAL_TEST_MODE) return mock.mockAdminPinPost(postId)
  return request('/admin/post/pin', { postId })
}

export async function adminUnpinPost(postId) {
  if (LOCAL_TEST_MODE) return mock.mockAdminUnpinPost(postId)
  return request('/admin/post/unpin', { postId })
}

export async function adminGetPendingAchievements() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetPendingAchievements()
  return request('/admin/achievement/pending')
}

export async function adminApproveAchievement(id, level) {
  if (LOCAL_TEST_MODE) return mock.mockAdminApproveAchievement(id, level)
  return request('/admin/achievement/approve', { achievementId: id, level })
}

export async function adminRejectAchievement(id, reason) {
  if (LOCAL_TEST_MODE) return mock.mockAdminRejectAchievement(id, reason)
  return request('/admin/achievement/reject', { achievementId: id, reason })
}

export async function adminGetUserList(keyword = '') {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetUserList(keyword)
  return request('/admin/user/list', { keyword })
}

export async function adminGetUserProfile(userId) {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetUserProfile(userId)
  return request('/admin/user/profile', { userId })
}

export async function adminScoreUser(userId, delta, reason) {
  if (LOCAL_TEST_MODE) return mock.mockAdminScoreUser(userId, delta, reason)
  return request('/admin/user/score', { userId, delta, reason })
}

export async function adminGenerateInvite() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGenerateInvite()
  return request('/admin/invite/generate')
}

export async function adminSuperPromoteUser(targetUserId) {
  if (LOCAL_TEST_MODE) return mock.mockAdminSuperPromoteUser(targetUserId)
  return request('/admin/super/promote-user', { targetUserId })
}

export async function adminGetEmotionPosts() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetEmotionPosts()
  return request('/admin/emotion/list')
}

export async function adminGetEmotionHistory() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetEmotionHistory()
  return request('/admin/emotion/history')
}

export async function adminGetReviewHistory() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetReviewHistory()
  return request('/admin/review/history')
}

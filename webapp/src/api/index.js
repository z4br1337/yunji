import { LOCAL_TEST_MODE, API_BASE_URL } from '../utils/config.js'
import * as mock from './mock.js'

async function request(path, data = {}, method = 'POST') {
  if (LOCAL_TEST_MODE) return null

  const token = localStorage.getItem('token') || ''
  const res = await fetch(API_BASE_URL + path, {
    method,
    headers: { 'Content-Type': 'application/json', 'Authorization': token ? `Bearer ${token}` : '' },
    body: method !== 'GET' ? JSON.stringify(data) : undefined
  })
  const json = await res.json()
  if (json.code !== 0) throw new Error(json.message || '请求失败')
  return json.data
}

export async function register(nickname, username, password) {
  if (LOCAL_TEST_MODE) return mock.mockRegister(nickname, username, password)
  const data = await request('/user/register', { nickname, username, password })
  return data
}

export async function login(username, password) {
  if (LOCAL_TEST_MODE) return mock.mockLogin(username, password)
  const data = await request('/user/login', { username, password })
  if (data.token) localStorage.setItem('token', data.token)
  return data.user || data
}

export async function getProfile() {
  if (LOCAL_TEST_MODE) return mock.mockGetProfile()
  return request('/user/profile')
}

export async function updateProfile(data) {
  if (LOCAL_TEST_MODE) return mock.mockUpdateProfile(data)
  return request('/user/profile', data)
}

export async function useInviteCode(code) {
  if (LOCAL_TEST_MODE) return mock.mockUseInviteCode(code)
  return request('/user/invite', { code })
}

export async function getPointsLog() {
  if (LOCAL_TEST_MODE) return mock.mockGetPointsLog()
  return request('/user/points-log')
}

export async function getPosts(params = {}) {
  if (LOCAL_TEST_MODE) return mock.mockGetPosts(params)
  const { page, pageSize, ...filterFields } = params
  return request('/post/list', { filter: filterFields, page: page || 1 })
}

export async function getPostDetail(postId) {
  if (LOCAL_TEST_MODE) return mock.mockGetPostDetail(postId)
  return request('/post/detail', { postId })
}

export async function createPost(data) {
  if (LOCAL_TEST_MODE) return mock.mockCreatePost(data)
  return request('/post/create', data)
}

export async function getComments(postId) {
  if (LOCAL_TEST_MODE) return mock.mockGetComments(postId)
  return request('/comment/list', { postId })
}

export async function addComment(postId, content) {
  if (LOCAL_TEST_MODE) return mock.mockAddComment(postId, content)
  return request('/comment/add', { postId, content })
}

export async function getAchievements(params = {}) {
  if (LOCAL_TEST_MODE) return mock.mockGetAchievements(params)
  return request('/achievement/list', params)
}

export async function createAchievement(data) {
  if (LOCAL_TEST_MODE) return mock.mockCreateAchievement(data)
  return request('/achievement/create', data)
}

export async function getGrowthBook(userId) {
  if (LOCAL_TEST_MODE) return mock.mockGetGrowthBook(userId)
  return request('/growth-book/get', { userId })
}

export async function setGrowthBookPublic(isPublic) {
  if (LOCAL_TEST_MODE) return mock.mockSetGrowthBookPublic(isPublic)
  return request('/growth-book/set-public', { isPublic })
}

export async function sendMessage(toId, content) {
  if (LOCAL_TEST_MODE) return mock.mockSendMessage(toId, content)
  return request('/message/send', { toId, content })
}

export async function getConversations() {
  if (LOCAL_TEST_MODE) return mock.mockGetConversations()
  return request('/message/conversations')
}

export async function getChatHistory(peerId) {
  if (LOCAL_TEST_MODE) return mock.mockGetChatHistory(peerId)
  return request('/message/history', { peerId })
}

export async function uploadImage(file) {
  if (LOCAL_TEST_MODE) return mock.mockUploadImage(file)
  const formData = new FormData()
  formData.append('file', file)
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

// ========== 管理员 API ==========

export async function adminGetReports() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetReports()
  return request('/admin/reports')
}

export async function adminOverridePost(postId, action) {
  if (LOCAL_TEST_MODE) return mock.mockAdminOverridePost(postId, action)
  return request('/admin/post/override', { postId, action })
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
  return request('/admin/achievement/approve', { id, level })
}

export async function adminRejectAchievement(id, reason) {
  if (LOCAL_TEST_MODE) return mock.mockAdminRejectAchievement(id, reason)
  return request('/admin/achievement/reject', { id, reason })
}

export async function adminGetUserList() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetUserList()
  return request('/admin/user/list')
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

export async function adminGetEmotionPosts() {
  if (LOCAL_TEST_MODE) return mock.mockAdminGetEmotionPosts()
  return request('/admin/emotion/list')
}

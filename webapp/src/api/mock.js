/**
 * Mock 数据层 —— 本地测试用，脱离服务器独立运行
 */
import { check as sensitiveCheck } from '../utils/sensitive.js'
import { EXP_RULES, SCHOOL_CLASSES } from '../utils/config.js'
import { calcPostExp, calcAchievementExp } from '../utils/level.js'

let _nextId = 100
const genId = () => 'mock_' + (_nextId++)
const now = () => new Date().toISOString()
const delay = (ms = 80) => new Promise(r => setTimeout(r, ms))

let _currentUserId = null

const _users = {
  test_user_001: {
    _id: 'test_user_001', username: 'testuser', password: '123456', email: '', studentId: '2025001001',
    nickname: '测试同学', class: '25行管1班', profileCompleted: true, role: 'user',
    exp: 80, score: 80, postCount: 3,
    achievementCounts: { moral: 0, intellectual: 0, physical: 1, aesthetic: 0, labor: 1 },
    growthBookPublic: false, inviteUsed: null,
    createdAt: '2026-03-01T08:00:00Z', updatedAt: '2026-03-10T08:00:00Z'
  },
  test_admin_001: {
    _id: 'test_admin_001', username: 'admin', password: '123456', email: '', studentId: '2025999001',
    nickname: '导生小王', class: '25行管1班', profileCompleted: true, role: 'admin',
    exp: 1200, score: 1200, postCount: 5,
    achievementCounts: { moral: 2, intellectual: 3, physical: 1, aesthetic: 0, labor: 0 },
    growthBookPublic: true, inviteUsed: 'ADMIN2026',
    createdAt: '2026-02-15T08:00:00Z', updatedAt: '2026-03-10T08:00:00Z'
  }
}

const _userByUsername = {}
function _rebuildUsernameIndex() {
  for (const key in _users) {
    if (_users[key].username) _userByUsername[_users[key].username] = key
  }
}
_rebuildUsernameIndex()

const _posts = [
  { _id: 'post_001', authorId: 'test_user_001', isAnonymous: false, visibleAuthorName: '测试同学', content: '大家好！这是云迹的第一条帖子，欢迎大家来交流~', images: [], category: 'cognition', status: 'published', pinned: false, pointsAwarded: 0, createdAt: '2026-03-10T09:00:00Z', updatedAt: '2026-03-10T09:00:00Z' },
  { _id: 'post_002', authorId: 'test_user_001', isAnonymous: true, visibleAuthorName: '匿名用户', content: '最近学业压力好大，感觉有点撑不住了…希望有人能理解。', images: [], category: 'emotion', status: 'published', pinned: false, pointsAwarded: 0, needOffline: false, offlineTime: '', offlinePlace: '', createdAt: '2026-03-10T10:30:00Z', updatedAt: '2026-03-10T10:30:00Z' },
  { _id: 'post_003', authorId: 'test_admin_001', isAnonymous: false, visibleAuthorName: '导生小王', content: '校运会志愿者招募开始了！有兴趣的同学可以在成果页提交德育成果哦~', images: [], category: 'knowledge', status: 'published', pinned: true, pointsAwarded: 0, createdAt: '2026-03-09T14:00:00Z', updatedAt: '2026-03-09T14:00:00Z' }
]

const _comments = [
  { _id: 'cmt_001', postId: 'post_001', authorId: 'test_admin_001', authorName: '导生小王', isAdmin: true, content: '欢迎使用云迹！', createdAt: '2026-03-10T09:30:00Z' },
  { _id: 'cmt_002', postId: 'post_002', authorId: 'test_admin_001', authorName: '导生小王', isAdmin: true, content: '同学你好，已看到你的倾诉。', createdAt: '2026-03-10T11:00:00Z' }
]

const _achievements = [
  { _id: 'ach_001', userId: 'test_user_001', title: '校运会100米短跑第三名', description: '在2026年春季校运会中获得百米第三名', category: 'physical', dimension: '', subcategory: '', level: 3, points: 0, expAwarded: 1500, images: [], status: 'approved', createdAt: '2026-03-08T10:00:00Z' },
  { _id: 'ach_002', userId: 'test_user_001', title: '参与校园清洁志愿活动', description: '连续3天参与图书馆外的绿化清洁', category: 'labor', dimension: '', subcategory: '', level: 2, points: 0, expAwarded: 1000, images: [], status: 'approved', createdAt: '2026-03-05T14:00:00Z' },
  { _id: 'ach_pending_001', userId: 'test_user_001', title: '待审核德育活动', description: '示例待审核成果', category: 'moral', dimension: '', subcategory: '', level: 2, points: 0, expAwarded: 0, images: [], status: 'pending', createdAt: '2026-03-10T12:00:00Z' }
]

const _pointsLog = [
  { _id: 'pl_001', userId: 'test_user_001', delta: 10, type: 'exp', reason: 'post_published', relatedId: 'post_001', createdAt: '2026-03-10T09:00:00Z' },
  { _id: 'pl_002', userId: 'test_user_001', delta: 10, type: 'exp', reason: 'create_account', relatedId: '', createdAt: '2026-03-01T08:00:00Z' }
]

const _invites = [
  { code: 'ADMIN2026', role: 'admin', usedBy: 'test_admin_001', createdAt: '2026-02-01T00:00:00Z' },
  { code: 'TESTCODE', role: 'admin', usedBy: null, createdAt: '2026-03-01T00:00:00Z' }
]

const _messages = []

/** mock 导生操作记录 */
let _adminLogs = []

function cur() { return _users[_currentUserId] || null }

function _authorClass(authorId) {
  const u = _users[authorId]
  return u ? (u.class || '').trim() : ''
}

function _adminClass() {
  const a = cur()
  return a ? (a.class || '').trim() : ''
}

function _pushAdminLog(action, targetType, targetId, detail) {
  const a = cur()
  if (!a || a.role !== 'admin') return
  _adminLogs.unshift({
    _id: genId(),
    action,
    targetType,
    targetId: String(targetId),
    detail: { ...detail, authorClass: detail.authorClass || _adminClass() },
    createdAt: now(),
  })
}

function addExp(user, amount, reason, relatedId) {
  user.exp = (user.exp || 0) + amount
  user.score = user.exp
  _pointsLog.unshift({ _id: genId(), userId: user._id, delta: amount, type: 'exp', reason, relatedId: relatedId || '', createdAt: now() })
}

function safeUser(u) {
  if (!u) return null
  const { password: _, ...rest } = u
  return rest
}

// ========== Auth ==========

export async function mockRegister(nickname, username, password) {
  await delay()
  if (!nickname || !username || !password) throw new Error('昵称、账号、密码均为必填')
  if (username.length < 3) throw new Error('账号长度至少 3 位')
  if (password.length < 6) throw new Error('密码长度至少 6 位')
  if (_userByUsername[username]) throw new Error('该账号已被注册')

  const id = genId()
  const user = {
    _id: id, username, password, nickname, email: '', studentId: '',
    class: '', profileCompleted: false, role: 'user',
    exp: 10, score: 10, postCount: 0,
    achievementCounts: {}, growthBookPublic: false, inviteUsed: null,
    createdAt: now(), updatedAt: now()
  }
  _users[id] = user
  _userByUsername[username] = id
  return { user: safeUser(user), token: id }
}

function _findUserIdByStudentId(raw) {
  const s = (raw || '').trim()
  if (!s) return null
  for (const id of Object.keys(_users)) {
    if ((_users[id].studentId || '').trim() === s) return id
  }
  return null
}

export async function mockLogin(username, password) {
  await delay()
  let userId = _userByUsername[username]
  if (!userId) userId = _findUserIdByStudentId(username)
  if (!userId) throw new Error('账号不存在')
  const user = _users[userId]
  if (user.password !== password) throw new Error('密码错误')
  _currentUserId = userId
  return safeUser(user)
}

export async function mockBindStudentId(studentId) {
  await delay()
  const user = cur()
  if (!user) throw new Error('请先登录')
  if ((user.studentId || '').trim()) throw new Error('已绑定学号')
  const sid = (studentId || '').trim()
  if (!/^[A-Za-z0-9_-]{4,32}$/.test(sid)) throw new Error('学号须为 4～32 位字母、数字、下划线或短横线')
  for (const id of Object.keys(_users)) {
    if (id === user._id) continue
    if ((_users[id].studentId || '').trim() === sid) throw new Error('该学号已被其他账号绑定')
  }
  user.studentId = sid
  user.updatedAt = now()
  return { user: safeUser(user) }
}

// ========== User ==========

export async function mockGetProfile() {
  await delay()
  return safeUser(cur())
}

export async function mockUpdateProfile(data) {
  await delay()
  const user = cur()
  if (!user) return {}
  if (data.nickname) user.nickname = data.nickname
  if (data.class !== undefined && data.class !== null) {
    const c = (data.class || '').trim()
    if (c && !SCHOOL_CLASSES.includes(c)) throw new Error('请从列表中选择合法班级')
    user.class = c
  }
  user.profileCompleted = !!(user.nickname && user.nickname.trim() && SCHOOL_CLASSES.includes(user.class))
  user.updatedAt = now()
  return { user: safeUser(user), profileCompleted: user.profileCompleted }
}

export async function mockUseInviteCode(code) {
  await delay()
  const inv = _invites.find(i => i.code === code)
  if (!inv) throw new Error('邀请码无效')
  if (inv.usedBy) throw new Error('邀请码已被使用')
  inv.usedBy = _currentUserId
  const user = cur()
  if (user) user.role = 'admin'
  return { role: 'admin' }
}

export async function mockGetPointsLog() {
  await delay()
  return { logs: _pointsLog.filter(l => l.userId === _currentUserId) }
}

// ========== Posts ==========

export async function mockGetPosts(params = {}) {
  await delay()
  const { category, page = 1, pageSize = 20, excludeEmotion, myPosts, keyword } = params
  const user = cur()
  const isAdmin = user && user.role === 'admin'
  const kw = (keyword || '').trim()

  let filtered = _posts.filter(p => {
    if (myPosts && p.authorId !== _currentUserId) return false
    if (myPosts && excludeEmotion && p.category === 'emotion') return false
    if (p.status === 'flagged' && !isAdmin) return false
    if (p.status === 'archived' && !isAdmin) return false
    if (excludeEmotion && p.category === 'emotion') return false
    if (p.category === 'emotion' && !isAdmin && p.authorId !== _currentUserId) return false
    if (category && category !== 'all' && p.category !== category) return false
    if (!isAdmin && p.status !== 'published' && p.authorId !== _currentUserId) return false
    if (kw && !(p.content || '').includes(kw)) return false
    return true
  })

  filtered.sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
    return new Date(b.createdAt) - new Date(a.createdAt)
  })

  const start = (page - 1) * pageSize
  return { posts: filtered.slice(start, start + pageSize), total: filtered.length, hasMore: start + pageSize < filtered.length }
}

export async function mockGetPostDetail(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) throw new Error('帖子不存在')
  const user = cur()
  if (post.category === 'emotion') {
    if (!user) throw new Error('请先登录')
    const isAdmin = user.role === 'admin'
    const isAuthor = post.authorId === user._id
    if (isAdmin) {
      const ac = _adminClass()
      if (!SCHOOL_CLASSES.includes(ac) || _authorClass(post.authorId) !== ac) {
        throw new Error('无权查看该情感倾诉')
      }
    } else if (!isAuthor) {
      throw new Error('无权查看该情感倾诉')
    }
  }
  const isAdmin = user && user.role === 'admin'
  const authorUser = _users[post.authorId]
  const postData = { ...post }
  if (isAdmin && authorUser) {
    postData.authorName = authorUser.nickname
    postData.authorClass = authorUser.class || ''
  }
  return { posts: [postData], total: 1, hasMore: false }
}

export async function mockCreatePost(data) {
  await delay()
  const content = (data.content || '').trim()
  if (!sensitiveCheck(content).pass) {
    throw new Error('内容包含敏感词，无法发布')
  }
  const user = cur()
  const post = {
    _id: genId(), authorId: _currentUserId,
    isAnonymous: !!data.isAnonymous,
    visibleAuthorName: data.isAnonymous ? '匿名用户' : (user ? user.nickname : '未知'),
    content: data.content, images: data.images || [],
    category: data.category || 'cognition',
    status: 'published', pinned: false, pointsAwarded: 0,
    needOffline: !!data.needOffline, offlineTime: data.offlineTime || '', offlinePlace: data.offlinePlace || '',
    flagged: false, flaggedWords: [], flaggedCategories: [], flaggedHighlighted: '',
    createdAt: now(), updatedAt: now()
  }
  _posts.unshift(post)

  if (user) {
    addExp(user, calcPostExp(), 'post_published', post._id)
    user.postCount = (user.postCount || 0) + 1
  }
  return { postId: post._id, expGain: EXP_RULES.POST_PUBLISH }
}

export async function mockDeletePost(postId) {
  await delay()
  const user = cur()
  const idx = _posts.findIndex(p => p._id === postId)
  if (idx < 0) throw new Error('帖子不存在')
  const post = _posts[idx]
  if (post.authorId !== _currentUserId) {
    if (!user || user.role !== 'admin') throw new Error('无权删除该帖子')
    const ac = _adminClass()
    if (!SCHOOL_CLASSES.includes(ac) || _authorClass(post.authorId) !== ac) {
      throw new Error('无权删除其他班级的帖子')
    }
  }
  const shouldDecr = (post.status === 'published' || post.status === 'archived') && !post.flagged
  const authorId = post.authorId
  _posts.splice(idx, 1)
  for (let i = _comments.length - 1; i >= 0; i--) {
    if (_comments[i].postId === postId) _comments.splice(i, 1)
  }
  if (shouldDecr) {
    const au = _users[authorId]
    if (au) au.postCount = Math.max(0, (au.postCount || 0) - 1)
  }
  return {}
}

// ========== Comments ==========

export async function mockGetComments(postId) {
  await delay()
  return { comments: _comments.filter(c => c.postId === postId) }
}

export async function mockAddComment(postId, content) {
  await delay()
  const user = cur()
  const post = _posts.find(p => p._id === postId)
  if (user && user.role === 'admin' && post) {
    const ac = _adminClass()
    if (!SCHOOL_CLASSES.includes(ac) || _authorClass(post.authorId) !== ac) {
      throw new Error('无权评论其他班级的帖子')
    }
  }
  const comment = { _id: genId(), postId, authorId: _currentUserId, authorName: user ? user.nickname : '未知', isAdmin: user ? user.role === 'admin' : false, content, createdAt: now() }
  _comments.push(comment)
  return { commentId: comment._id }
}

// ========== Achievements ==========

export async function mockGetAchievements(params = {}) {
  await delay()
  const { status, category, userId } = params
  const filtered = _achievements.filter(a => {
    if (status && a.status !== status) return false
    if (category && a.category !== category) return false
    return a.userId === (userId || _currentUserId)
  })
  return { achievements: filtered }
}

export async function mockCreateAchievement(data) {
  await delay()
  const ach = { _id: genId(), userId: _currentUserId, title: data.title, description: data.description || '', category: data.category, dimension: data.dimension || '', subcategory: data.subcategory || '', level: data.level || 1, points: 0, expAwarded: 0, images: data.images || [], status: 'pending', createdAt: now() }
  _achievements.unshift(ach)
  return { achievementId: ach._id, status: 'pending' }
}

// ========== Growth Book ==========

export async function mockGetGrowthBook(userId) {
  await delay()
  const uid = userId || _currentUserId
  const viewer = cur()
  const isOwner = uid === _currentUserId
  const isAdmin = viewer && viewer.role === 'admin'
  const target = _users[uid]
  if (!target) throw new Error('用户不存在')
  if (!isOwner && !isAdmin && !target.growthBookPublic) throw new Error('该用户的成长手册未公开')
  const achs = _achievements.filter(a => a.userId === uid && a.status === 'approved')
  return { achievements: achs, user: { nickname: target.nickname, class: target.class, exp: target.exp, achievementCounts: target.achievementCounts, postCount: target.postCount }, isOwner, growthBookPublic: target.growthBookPublic }
}

export async function mockSetGrowthBookPublic(isPublic) {
  await delay()
  const user = cur()
  if (user) { user.growthBookPublic = !!isPublic; user.updatedAt = now() }
  return {}
}

// ========== Messages ==========

export async function mockSendMessage(toId, content) {
  await delay()
  const user = cur()
  const msg = { _id: genId(), fromId: _currentUserId, fromName: user ? user.nickname : '未知', toId, content, read: false, createdAt: now() }
  _messages.push(msg)
  return { messageId: msg._id }
}

export async function mockGetConversations() {
  await delay()
  const convMap = {}
  for (const m of _messages) {
    if (m.fromId !== _currentUserId && m.toId !== _currentUserId) continue
    const peerId = m.fromId === _currentUserId ? m.toId : m.fromId
    if (!convMap[peerId] || convMap[peerId].createdAt < m.createdAt) convMap[peerId] = m
  }
  const list = Object.keys(convMap).map(pid => {
    const last = convMap[pid]
    const peer = _users[pid]
    const unread = _messages.filter(mm => mm.fromId === pid && mm.toId === _currentUserId && !mm.read).length
    return { peerId: pid, peerName: peer ? peer.nickname : '未知用户', peerClass: peer ? peer.class : '', lastContent: last.content, lastTime: last.createdAt, unreadCount: unread }
  })
  list.sort((a, b) => a.lastTime < b.lastTime ? 1 : -1)
  return { conversations: list }
}

export async function mockGetChatHistory(peerId) {
  await delay()
  const history = _messages.filter(m => (m.fromId === _currentUserId && m.toId === peerId) || (m.fromId === peerId && m.toId === _currentUserId))
  history.forEach(m => { if (m.toId === _currentUserId) m.read = true })
  return { messages: history }
}

export async function mockUploadImage(file) {
  await delay(50)
  return { url: URL.createObjectURL(file) }
}

// ========== Admin ==========

export async function mockAdminGetReports() {
  await delay()
  const ac = _adminClass()
  const inClass = (p) => _authorClass(p.authorId) === ac && SCHOOL_CLASSES.includes(ac)
  const base = _posts.filter(p => inClass(p) && p.category !== 'emotion')
  return {
    flagged: base.filter(p => p.status === 'flagged'),
    allPosts: base,
    posts: base,
    total: base.length,
    hasMore: false,
  }
}

export async function mockAdminOverridePost(postId, action) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) return {}
  const ac = _adminClass()
  if (_authorClass(post.authorId) !== ac || !SCHOOL_CLASSES.includes(ac)) throw new Error('无权操作其他班级的帖子')
  post.status = action
  post.updatedAt = now()
  const au = _users[post.authorId]
  _pushAdminLog('post_override', 'post', postId, {
    newStatus: action,
    summary: (post.content || '').slice(0, 120),
    authorNickname: au ? au.nickname : '',
    authorClass: au ? au.class : ac,
  })
  return {}
}

export async function mockAdminPinPost(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) return {}
  const ac = _adminClass()
  if (_authorClass(post.authorId) !== ac || !SCHOOL_CLASSES.includes(ac)) throw new Error('无权操作')
  post.pinned = true
  post.updatedAt = now()
  return {}
}

export async function mockAdminUnpinPost(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) return {}
  const ac = _adminClass()
  if (_authorClass(post.authorId) !== ac || !SCHOOL_CLASSES.includes(ac)) throw new Error('无权操作')
  post.pinned = false
  post.updatedAt = now()
  return {}
}

export async function mockAdminGetPendingAchievements() {
  await delay()
  const ac = _adminClass()
  return {
    achievements: _achievements.filter(
      a => a.status === 'pending' && _authorClass(a.userId) === ac && SCHOOL_CLASSES.includes(ac)
    ),
  }
}

export async function mockAdminApproveAchievement(id, level) {
  await delay()
  const ach = _achievements.find(a => a._id === id)
  if (!ach) return {}
  const ac = _adminClass()
  if (_authorClass(ach.userId) !== ac || !SCHOOL_CLASSES.includes(ac)) throw new Error('无权审核其他班级的成果')
  ach.status = 'approved'
  if (level) ach.level = level
  const user = _users[ach.userId]
  if (user) {
    const expGain = calcAchievementExp(ach.level)
    ach.expAwarded = expGain
    addExp(user, expGain, 'achievement_approved', ach._id)
    if (!user.achievementCounts) user.achievementCounts = {}
    user.achievementCounts[ach.category] = (user.achievementCounts[ach.category] || 0) + 1
  }
  _pushAdminLog('achievement_approve', 'achievement', id, {
    title: ach.title,
    authorNickname: user ? user.nickname : '',
    authorClass: user ? user.class : ac,
    expGain: ach.expAwarded,
  })
  return { expGain: ach.expAwarded }
}

export async function mockAdminRejectAchievement(id) {
  await delay()
  const ach = _achievements.find(a => a._id === id)
  if (!ach) return {}
  const ac = _adminClass()
  if (_authorClass(ach.userId) !== ac || !SCHOOL_CLASSES.includes(ac)) throw new Error('无权审核其他班级的成果')
  ach.status = 'rejected'
  const user = _users[ach.userId]
  _pushAdminLog('achievement_reject', 'achievement', id, {
    title: ach.title,
    authorNickname: user ? user.nickname : '',
    authorClass: user ? user.class : ac,
  })
  return {}
}

export async function mockAdminGetUserList(keyword) {
  await delay()
  const kw = (keyword || '').trim().toLowerCase()
  let list = Object.values(_users)
  if (kw) {
    list = list.filter(u =>
      (u.nickname && u.nickname.toLowerCase().includes(kw))
      || (u.username && u.username.toLowerCase().includes(kw))
      || (u._id && u._id.toLowerCase().includes(kw))
      || (u.class && u.class.toLowerCase().includes(kw))
      || (u.studentId && String(u.studentId).toLowerCase().includes(kw))
    )
  }
  return { users: list.map(safeUser) }
}

export async function mockAdminGetUserProfile(userId) {
  await delay()
  const user = _users[userId]
  if (!user) throw new Error('用户不存在')
  const postCount = _posts.filter(p => p.authorId === userId).length
  const achCount = _achievements.filter(a => a.userId === userId).length
  const logs = _pointsLog.filter(l => l.userId === userId).slice(0, 10)
  return { user: safeUser(user), stats: { postCount, achievementCount: achCount }, recentPointsLog: logs }
}

export async function mockAdminScoreUser(userId, delta) {
  await delay()
  const user = _users[userId]
  if (user) addExp(user, delta, 'admin_score', '')
  return { pointsDelta: delta }
}

export async function mockAdminGenerateInvite() {
  await delay()
  const code = 'INV' + Math.random().toString(36).substring(2, 8).toUpperCase()
  _invites.push({ code, role: 'admin', usedBy: null, createdAt: now() })
  return { inviteCode: code }
}

export async function mockAdminGetEmotionPosts() {
  await delay()
  const ac = _adminClass()
  return {
    posts: _posts.filter(
      p => p.category === 'emotion' && _authorClass(p.authorId) === ac && SCHOOL_CLASSES.includes(ac)
    ),
  }
}

export async function mockAdminGetEmotionHistory() {
  await delay()
  const ac = _adminClass()
  const aid = _currentUserId
  return {
    posts: _posts.filter(p => {
      if (p.category !== 'emotion' || _authorClass(p.authorId) !== ac) return false
      return _comments.some(
        c => c.postId === p._id && c.authorId === aid && c.isAdmin
      )
    }),
  }
}

export async function mockAdminGetReviewHistory() {
  await delay()
  const ac = _adminClass()
  const logs = _adminLogs.filter(l => (l.detail && l.detail.authorClass) === ac)
  return { logs }
}

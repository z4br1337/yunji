/**
 * Mock 数据层 —— 本地测试用，脱离服务器独立运行
 */
import { check as sensitiveCheck } from '../utils/sensitive.js'
import { SCHOOL_CLASSES } from '../utils/config.js'
import { calcPostExp, calcAchievementExp } from '../utils/level.js'

let _nextId = 100
const genId = () => 'mock_' + (_nextId++)
const now = () => new Date().toISOString()
const delay = (ms = 80) => new Promise(r => setTimeout(r, ms))

let _currentUserId = null

/** 近期活动 mock（数组；isActive 为 true 的最多一条用于广场入口） */
let _mockCampaigns = [
  {
    _id: 'mock_camp_1',
    title: '校园主题周',
    intro: '在发帖时为帖子添加话题 #云迹广场#，分享你的校园故事。',
    backgroundUrl: '',
    tag: '云迹广场',
    isActive: true,
    updatedAt: now(),
  },
]

function _mockActiveCampaignRow() {
  return _mockCampaigns.find((c) => c.isActive && String(c.tag || '').trim()) || null
}

function _mockCampaignToClient(c) {
  if (!c) return null
  return {
    _id: c._id,
    title: c.title,
    intro: c.intro,
    backgroundUrl: c.backgroundUrl || '',
    tag: c.tag,
    isActive: !!c.isActive,
    updatedAt: c.updatedAt || now(),
  }
}

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
  },
  dup_user_a: {
    _id: 'dup_user_a', username: 'dupa', password: '123456', email: '', studentId: 'SHARED2026',
    nickname: '同学甲-同学号', class: '25行管1班', profileCompleted: true, role: 'user',
    exp: 20, score: 20, postCount: 0,
    achievementCounts: {}, growthBookPublic: false, inviteUsed: null,
    avatarUrl: '', createdAt: '2026-03-01T08:00:00Z', updatedAt: '2026-03-10T08:00:00Z'
  },
  dup_user_b: {
    _id: 'dup_user_b', username: 'dupb', password: '123456', email: '', studentId: 'SHARED2026',
    nickname: '同学乙-同学号', class: '25行管1班', profileCompleted: true, role: 'user',
    exp: 20, score: 20, postCount: 0,
    achievementCounts: {}, growthBookPublic: false, inviteUsed: null,
    avatarUrl: '', createdAt: '2026-03-01T08:00:00Z', updatedAt: '2026-03-10T08:00:00Z'
  },
  super_zsb_mock: {
    _id: 'super_zsb_mock', username: 'daoshengzsb0125', password: '123456', email: '', studentId: '2026000999',
    nickname: '最高管理(mock)', class: '25行管1班', profileCompleted: true, role: 'admin',
    exp: 100, score: 100, postCount: 0,
    achievementCounts: {}, growthBookPublic: true, inviteUsed: null,
    avatarUrl: '', createdAt: '2026-01-01T08:00:00Z', updatedAt: '2026-03-10T08:00:00Z'
  }
}

const _userByUsername = {}
function _rebuildUsernameIndex() {
  for (const key in _users) {
    if (_users[key].username) _userByUsername[_users[key].username] = key
  }
}
_rebuildUsernameIndex()

const _postLikes = new Set() // `${userId}:${postId}`

const _posts = [
  { _id: 'post_001', authorId: 'test_user_001', isAnonymous: false, visibleAuthorName: '测试同学', content: '大家好！这是云迹的第一条帖子，欢迎大家来交流~', images: [], topics: ['云迹广场', '新生'], category: 'cognition', status: 'published', pinned: false, featured: false, likeCount: 2, pointsAwarded: 0, createdAt: '2026-03-10T09:00:00Z', updatedAt: '2026-03-10T09:00:00Z' },
  { _id: 'post_002', authorId: 'test_user_001', isAnonymous: true, visibleAuthorName: '匿名用户', content: '最近学业压力好大，感觉有点撑不住了…希望有人能理解。', images: [], topics: [], category: 'emotion', status: 'published', pinned: false, featured: false, likeCount: 0, pointsAwarded: 0, needOffline: false, offlineTime: '', offlinePlace: '', createdAt: '2026-03-10T10:30:00Z', updatedAt: '2026-03-10T10:30:00Z' },
  { _id: 'post_003', authorId: 'test_admin_001', isAnonymous: false, visibleAuthorName: '导生小王', content: '校运会志愿者招募开始了！有兴趣的同学可以在成果页提交德育成果哦~', images: [], topics: ['校运会', '志愿者'], category: 'knowledge', status: 'published', pinned: true, featured: true, likeCount: 5, pointsAwarded: 0, createdAt: '2026-03-09T14:00:00Z', updatedAt: '2026-03-09T14:00:00Z' },
  { _id: 'post_004', authorId: 'test_user_001', isAnonymous: false, visibleAuthorName: '测试同学', content: '这是一条高赞帖（用于展示自动精品样式）。', images: [], topics: ['云迹广场'], category: 'cognition', status: 'published', pinned: false, featured: false, likeCount: 35, pointsAwarded: 0, createdAt: '2026-03-08T12:00:00Z', updatedAt: '2026-03-08T12:00:00Z' },
]

const _fileShareLikes = new Set() // `${userId}:${fileId}`

const _mockFileShares = [
  {
    _id: 'fs_001',
    userId: 'test_user_001',
    title: '高等数学复习笔记',
    description: 'Mock 示例文件',
    fileUrl: 'https://example.com/mock-note.pdf',
    fileName: 'note.pdf',
    status: 'approved',
    likeCount: 2,
    createdAt: '2026-03-08T09:00:00Z',
  },
]

/** 个人主页留言 profileOwnerId -> 展示在某用户主页 */
const _wallMessages = []

function _postBoutique(p) {
  return !!(p.category !== 'emotion' && (p.likeCount || 0) > 30)
}

const _comments = [
  { _id: 'cmt_001', postId: 'post_001', authorId: 'test_admin_001', authorName: '导生小王', isAdmin: true, content: '欢迎使用云迹！', parentCommentId: '', parentAuthorName: '', createdAt: '2026-03-10T09:30:00Z' },
  { _id: 'cmt_002', postId: 'post_002', authorId: 'test_admin_001', authorName: '导生小王', isAdmin: true, content: '同学你好，已看到你的倾诉。', parentCommentId: '', parentAuthorName: '', createdAt: '2026-03-10T11:00:00Z' }
]

/** 当前用户互动「已读」水位（mock） */
const _interactionSeenByUser = {}

function _interactionSeen() {
  const uid = _currentUserId
  if (!uid) return { replyAt: new Date().toISOString(), postAt: new Date().toISOString() }
  if (!_interactionSeenByUser[uid]) {
    _interactionSeenByUser[uid] = { replyAt: '2020-01-01T00:00:00.000Z', postAt: '2020-01-01T00:00:00.000Z' }
  }
  return _interactionSeenByUser[uid]
}

function _removeCommentCascade(commentId) {
  const remove = new Set([commentId])
  let growing = true
  while (growing) {
    growing = false
    for (const c of _comments) {
      if (c.parentCommentId && remove.has(c.parentCommentId) && !remove.has(c._id)) {
        remove.add(c._id)
        growing = true
      }
    }
  }
  for (let i = _comments.length - 1; i >= 0; i--) {
    if (remove.has(_comments[i]._id)) _comments.splice(i, 1)
  }
}

const _achievements = [
  { _id: 'ach_001', userId: 'test_user_001', title: '校运会100米短跑第三名', description: '在2026年春季校运会中获得百米第三名', category: 'physical', dimension: '', subcategory: '', level: 3, points: 0, expAwarded: 1500, images: [], status: 'approved', createdAt: '2026-03-08T10:00:00Z' },
  { _id: 'ach_002', userId: 'test_user_001', title: '参与校园清洁志愿活动', description: '连续3天参与图书馆外的绿化清洁', category: 'labor', dimension: '', subcategory: '', level: 2, points: 0, expAwarded: 1000, images: [], status: 'approved', createdAt: '2026-03-05T14:00:00Z' },
  { _id: 'ach_pending_001', userId: 'test_user_001', title: '待审核德育活动', description: '示例待审核成果', category: 'moral', dimension: '', subcategory: '', level: 2, points: 0, expAwarded: 0, images: [], status: 'pending', createdAt: '2026-03-10T12:00:00Z' },
  { _id: 'ach_003', userId: 'test_admin_001', title: '组织班级读书会', description: '作为导生组织本班读书分享活动', category: 'intellectual', dimension: '', subcategory: '', level: 2, points: 0, expAwarded: 1000, images: [], status: 'approved', createdAt: '2026-03-07T10:00:00Z' }
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

const MOCK_SUPER_ADMIN_USERNAME = 'daoshengzsb0125'

function isMockSuperAdmin(u) {
  return !!(u && u.username === MOCK_SUPER_ADMIN_USERNAME)
}

/** 导生是否可操作该作者所在班级范围（最高管理员视为全站） */
function _mockAdminActsOnAuthor(authorId) {
  const admin = cur()
  if (!admin || admin.role !== 'admin') return false
  if (isMockSuperAdmin(admin)) return true
  const ac = (admin.class || '').trim()
  return SCHOOL_CLASSES.includes(ac) && _authorClass(authorId) === ac
}

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
  return { ...rest, isSuperAdmin: u.username === MOCK_SUPER_ADMIN_USERNAME }
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

function _findUserIdsByStudentId(raw) {
  const s = (raw || '').trim()
  if (!s) return []
  return Object.keys(_users).filter(id => (_users[id].studentId || '').trim() === s)
}

export async function mockLogin(identifier, password) {
  await delay()
  let candidateIds = []
  if (_userByUsername[identifier]) {
    candidateIds = [_userByUsername[identifier]]
  } else {
    candidateIds = _findUserIdsByStudentId(identifier)
  }
  if (!candidateIds.length) throw new Error('账号不存在')
  const matching = candidateIds
    .map(id => _users[id])
    .filter(u => u && u.password === password)
  if (!matching.length) throw new Error('密码错误')
  if (matching.length > 1) {
    return {
      __pickAccount: true,
      accounts: matching.map(u => ({
        username: u.username,
        nickname: u.nickname,
        avatarUrl: u.avatarUrl || '',
      })),
    }
  }
  const user = matching[0]
  if (user.username === MOCK_SUPER_ADMIN_USERNAME && user.role !== 'admin') {
    user.role = 'admin'
  }
  _currentUserId = user._id
  return safeUser(user)
}

export async function mockBindStudentId(studentId) {
  await delay()
  const user = cur()
  if (!user) throw new Error('请先登录')
  if ((user.studentId || '').trim()) throw new Error('已绑定学号')
  const sid = (studentId || '').trim()
  if (!/^[A-Za-z0-9_-]{4,32}$/.test(sid)) throw new Error('学号须为 4～32 位字母、数字、下划线或短横线')
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

function _normalizeTopicsMock(raw) {
  if (!raw || !Array.isArray(raw)) return []
  const out = []
  const seen = new Set()
  for (const x of raw) {
    const s = String(x || '').trim().replace(/#/g, '').replace(/\|/g, '').replace(/\n/g, '').slice(0, 24)
    if (!s || seen.has(s)) continue
    seen.add(s)
    out.push(s)
    if (out.length >= 5) break
  }
  return out
}

export async function mockGetPosts(params = {}) {
  await delay()
  const { category, page = 1, pageSize = 20, excludeEmotion, myPosts, keyword, authorId, topic } = params
  const user = cur()
  const isAdmin = user && user.role === 'admin'
  const kw = (keyword || '').trim()

  let filtered = _posts.filter(p => {
    if (authorId && p.authorId !== authorId) return false
    if (authorId && p.category === 'emotion') return false
    if (myPosts && p.authorId !== _currentUserId) return false
    if (myPosts && excludeEmotion && p.category === 'emotion') return false
    if (p.status === 'flagged' && !isAdmin) return false
    if (p.status === 'archived' && !isAdmin) return false
    if (excludeEmotion && p.category === 'emotion') return false
    if (p.category === 'emotion' && !isAdmin && p.authorId !== _currentUserId) return false
    if (category && category !== 'all' && p.category !== category) return false
    if (!isAdmin && p.status !== 'published' && p.authorId !== _currentUserId) return false
    if (kw && !(p.content || '').includes(kw)) return false
    if (topic && String(topic).trim()) {
      const tf = String(topic).trim()
      if (!(p.topics || []).includes(tf)) return false
    }
    return true
  })

  if (myPosts || authorId) {
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  } else if (category !== 'emotion') {
    filtered.sort((a, b) => {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
      if (a.featured !== b.featured) return a.featured ? -1 : 1
      const lc = (b.likeCount || 0) - (a.likeCount || 0)
      if (lc !== 0) return lc
      return new Date(b.createdAt) - new Date(a.createdAt)
    })
  } else {
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  }

  const start = (page - 1) * pageSize
  const slice = filtered.slice(start, start + pageSize).map((p) => ({
    ...p,
    boutique: _postBoutique(p),
    likedByMe: _postLikes.has(`${_currentUserId}:${p._id}`),
  }))
  return { posts: slice, total: filtered.length, hasMore: start + pageSize < filtered.length }
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
      if (!isMockSuperAdmin(user)) {
        const ac = _adminClass()
        if (!SCHOOL_CLASSES.includes(ac) || _authorClass(post.authorId) !== ac) {
          throw new Error('无权查看该情感倾诉')
        }
      }
    } else if (!isAuthor) {
      throw new Error('无权查看该情感倾诉')
    }
  }
  const isAdmin = user && user.role === 'admin'
  const authorUser = _users[post.authorId]
  const postData = {
    ...post,
    topics: Array.isArray(post.topics) ? [...post.topics] : [],
    likeCount: post.likeCount || 0,
    featured: !!post.featured,
    boutique: _postBoutique(post),
    likedByMe: _currentUserId ? _postLikes.has(`${_currentUserId}:${postId}`) : false,
  }
  if (isAdmin && authorUser) {
    postData.authorName = authorUser.nickname
    postData.authorClass = authorUser.class || ''
    postData.authorStudentId = (authorUser.studentId || '').trim()
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
  const topics = _normalizeTopicsMock(data.topics)
  for (const t of topics) {
    if (!sensitiveCheck(t).pass) throw new Error('话题包含敏感词')
  }
  const post = {
    _id: genId(), authorId: _currentUserId,
    isAnonymous: !!data.isAnonymous,
    visibleAuthorName: data.isAnonymous ? '匿名用户' : (user ? user.nickname : '未知'),
    content: data.content, images: data.images || [], topics,
    category: data.category || 'cognition',
    status: 'published', pinned: false, featured: false, likeCount: 0, pointsAwarded: 0,
    needOffline: !!data.needOffline, offlineTime: data.offlineTime || '', offlinePlace: data.offlinePlace || '',
    flagged: false, flaggedWords: [], flaggedCategories: [], flaggedHighlighted: '',
    createdAt: now(), updatedAt: now()
  }
  _posts.unshift(post)

  const activeCamp = _mockActiveCampaignRow()
  const baseExp = calcPostExp()
  let expAmt = baseExp
  let reason = 'post_published'
  if (activeCamp && activeCamp.tag && topics.includes(activeCamp.tag)) {
    expAmt = baseExp * 5
    reason = 'post_activity'
  }
  if (user) {
    addExp(user, expAmt, reason, post._id)
    user.postCount = (user.postCount || 0) + 1
  }
  return { postId: post._id, expGain: expAmt }
}

export async function mockDeletePost(postId) {
  await delay()
  const user = cur()
  const idx = _posts.findIndex(p => p._id === postId)
  if (idx < 0) throw new Error('帖子不存在')
  const post = _posts[idx]
  if (post.authorId !== _currentUserId) {
    if (!user || user.role !== 'admin') throw new Error('无权删除该帖子')
    if (!_mockAdminActsOnAuthor(post.authorId)) {
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

export async function mockAddComment(postId, content, opts = {}) {
  await delay()
  const text = (content || '').trim()
  if (!text) throw new Error('评论不能为空')
  if (!sensitiveCheck(text).pass) {
    throw new Error('评论包含敏感词，无法发送')
  }
  const user = cur()
  const post = _posts.find(p => p._id === postId)
  if (user && user.role === 'admin' && post && post.category === 'emotion') {
    if (!_mockAdminActsOnAuthor(post.authorId)) {
      throw new Error('无权评论该情感倾诉')
    }
  }
  let parentCommentId = ''
  let parentAuthorName = ''
  const rawParent = opts && (opts.parentCommentId || opts.replyToCommentId)
  if (rawParent) {
    const par = _comments.find(x => x._id === String(rawParent))
    if (!par || par.postId !== postId) throw new Error('回复的评论不存在')
    parentCommentId = par._id
    parentAuthorName = par.authorName || ''
  }
  const comment = {
    _id: genId(), postId, authorId: _currentUserId, authorName: user ? user.nickname : '未知',
    isAdmin: user ? user.role === 'admin' : false, content: text,
    parentCommentId, parentAuthorName, createdAt: now(),
  }
  _comments.push(comment)
  return { commentId: comment._id }
}

export async function mockDeleteComment(commentId) {
  await delay()
  const user = cur()
  const idx = _comments.findIndex(c => c._id === commentId)
  if (idx < 0) throw new Error('评论不存在')
  const c = _comments[idx]
  const post = _posts.find(p => p._id === c.postId)
  if (c.authorId === _currentUserId) {
    _removeCommentCascade(commentId)
    return {}
  }
  if (!user || user.role !== 'admin') throw new Error('无权删除该评论')
  if (post && post.category === 'emotion' && !_mockAdminActsOnAuthor(post.authorId)) {
    throw new Error('无权删除该评论')
  }
  _removeCommentCascade(commentId)
  return {}
}

// ========== Achievements ==========

export async function mockGetAchievements(params = {}) {
  await delay()
  if (params.community) {
    const filtered = _achievements.filter(a => {
      if (a.status !== 'approved') return false
      const u = _users[a.userId]
      if (!u || !u.growthBookPublic) return false
      if (params.category && a.category !== params.category) return false
      return true
    })
    return {
      achievements: filtered.map(a => ({
        ...a,
        authorNickname: _users[a.userId]?.nickname || '',
        authorClass: _users[a.userId]?.class || '',
      })),
    }
  }
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
  if (!target.growthBookPublic && !isOwner) {
    if (isAdmin && (isMockSuperAdmin(viewer) || (viewer.class && _authorClass(uid) === (viewer.class || '').trim()))) {
      // 最高管理员或同班导生
    } else {
      throw new Error('该用户的成长手册未公开')
    }
  }
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

export async function mockInteractionUnreadSummary() {
  await delay()
  const uid = _currentUserId
  if (!uid) return { dmUnread: 0, replyUnread: 0, postCommentUnread: 0, total: 0 }
  const seen = _interactionSeen()
  const dmUnread = _messages.filter(m => m.toId === uid && !m.read).length
  const replyUnread = _comments.filter(c => {
    if (!c.parentCommentId || c.authorId === uid) return false
    const par = _comments.find(p => p._id === c.parentCommentId)
    if (!par || par.authorId !== uid) return false
    return new Date(c.createdAt) > new Date(seen.replyAt)
  }).length
  const postCommentUnread = _comments.filter(c => {
    if (c.authorId === uid) return false
    const post = _posts.find(p => p._id === c.postId)
    if (!post || post.authorId !== uid) return false
    return new Date(c.createdAt) > new Date(seen.postAt)
  }).length
  return {
    dmUnread,
    replyUnread,
    postCommentUnread,
    total: dmUnread + replyUnread + postCommentUnread,
  }
}

export async function mockInteractionMarkSeen(scope = 'all') {
  await delay()
  const uid = _currentUserId
  if (!uid) return {}
  const seen = _interactionSeen()
  const t = now()
  if (scope === 'dm' || scope === 'all') {
    _messages.forEach(m => { if (m.toId === uid) m.read = true })
  }
  if (scope === 'reply' || scope === 'all') seen.replyAt = t
  if (scope === 'post_comment' || scope === 'all') seen.postAt = t
  return {}
}

export async function mockRepliesToMe() {
  await delay()
  const uid = _currentUserId
  const items = []
  for (const c of _comments) {
    if (!c.parentCommentId || c.authorId === uid) continue
    const par = _comments.find(p => p._id === c.parentCommentId)
    if (!par || par.authorId !== uid) continue
    const post = _posts.find(p => p._id === c.postId)
    items.push({
      commentId: c._id,
      fromId: c.authorId,
      fromName: c.authorName,
      fromAvatarUrl: _users[c.authorId]?.avatarUrl || '',
      replyContent: c.content,
      parentContent: (par.content || '').slice(0, 200),
      postId: c.postId,
      postSnippet: (post?.content || '').slice(0, 100),
      createdAt: c.createdAt,
    })
  }
  items.sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1))
  return { items: items.slice(0, 80) }
}

export async function mockCommentsOnMyPosts() {
  await delay()
  const uid = _currentUserId
  const items = []
  for (const c of _comments) {
    if (c.authorId === uid) continue
    const post = _posts.find(p => p._id === c.postId)
    if (!post || post.authorId !== uid) continue
    const par = c.parentCommentId ? _comments.find(p => p._id === c.parentCommentId) : null
    items.push({
      commentId: c._id,
      fromId: c.authorId,
      fromName: c.authorName,
      fromAvatarUrl: _users[c.authorId]?.avatarUrl || '',
      content: c.content,
      parentAuthorName: par ? (par.authorName || '') : '',
      postId: c.postId,
      postSnippet: (post?.content || '').slice(0, 100),
      createdAt: c.createdAt,
    })
  }
  items.sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1))
  return { items: items.slice(0, 80) }
}

export async function mockUploadImage(file) {
  await delay(50)
  return { url: URL.createObjectURL(file) }
}

export async function mockGetHotTopics() {
  await delay()
  const c = {}
  for (const p of _posts) {
    if (p.status !== 'published' || p.category === 'emotion') continue
    for (const t of p.topics || []) {
      const s = String(t).trim()
      if (s) c[s] = (c[s] || 0) + 1
    }
  }
  const topics = Object.entries(c).sort((a, b) => b[1] - a[1]).map((x) => x[0]).slice(0, 20)
  return { topics }
}

export async function mockGetHotPostSnippets() {
  await delay()
  const list = _posts
    .filter((p) => p.status === 'published' && p.category !== 'emotion')
    .sort((a, b) => (b.likeCount || 0) - (a.likeCount || 0) || String(b.createdAt).localeCompare(String(a.createdAt)))
    .slice(0, 20)
  const posts = list.map((p) => {
    let text = String(p.content || '').trim().replace(/\n/g, ' ')
    if (text.length > 72) text = text.slice(0, 72) + '…'
    return { _id: p._id, snippet: text || '（无文字）' }
  })
  return { posts }
}

export async function mockGetActivityCampaign() {
  await delay()
  const c = _mockActiveCampaignRow()
  if (!c) return { campaign: null }
  return { campaign: _mockCampaignToClient(c) }
}

export async function mockListActivityCampaigns() {
  await delay()
  const uid = _currentUserId
  const u = uid && _users[uid]
  if (!u || u.role !== 'admin') throw new Error('需要导生权限')
  const list = [..._mockCampaigns].sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')))
  return { campaigns: list.map(_mockCampaignToClient) }
}

export async function mockDeleteActivityCampaign(campaignId) {
  await delay()
  const uid = _currentUserId
  const u = uid && _users[uid]
  if (!u || u.role !== 'admin') throw new Error('需要导生权限')
  const id = String(campaignId || '')
  const idx = _mockCampaigns.findIndex((c) => String(c._id) === id)
  if (idx < 0) throw new Error('活动不存在')
  _mockCampaigns.splice(idx, 1)
  return {}
}

export async function mockSaveActivityCampaign(data) {
  await delay()
  const uid = _currentUserId
  const u = uid && _users[uid]
  if (!u || u.role !== 'admin') throw new Error('需要导生权限')
  const title = String(data.title || '').trim()
  const intro = String(data.intro || '').trim()
  const backgroundUrl = String(data.backgroundUrl || '').trim()
  const tag = String(data.tag || '').trim().replace(/#/g, '').slice(0, 24)
  if (!title) throw new Error('请填写活动名称')
  if (!tag) throw new Error('请填写活动 tag')
  if (!sensitiveCheck(title).pass) throw new Error('活动名称包含敏感词')
  if (intro && !sensitiveCheck(intro).pass) throw new Error('活动简介包含敏感词')
  if (!sensitiveCheck(tag).pass) throw new Error('活动 tag 包含敏感词')
  let wantActive = data.isActive
  if (wantActive === undefined || wantActive === null) wantActive = true
  else wantActive = !!wantActive

  const cid = data.campaignId || data.id
  if (cid) {
    const row = _mockCampaigns.find((c) => String(c._id) === String(cid))
    if (!row) throw new Error('活动不存在')
    row.title = title
    row.intro = intro
    row.backgroundUrl = backgroundUrl
    row.tag = tag
    row.updatedAt = now()
    if (wantActive) {
      _mockCampaigns.forEach((c) => { c.isActive = false })
      row.isActive = true
    } else {
      row.isActive = false
    }
    return await mockGetActivityCampaign()
  }

  if (wantActive) {
    _mockCampaigns.forEach((c) => { c.isActive = false })
  }
  _mockCampaigns.unshift({
    _id: genId(),
    title,
    intro,
    backgroundUrl,
    tag,
    isActive: wantActive,
    updatedAt: now(),
  })
  return await mockGetActivityCampaign()
}

export async function mockGetUserPublicHome(userId) {
  await delay()
  const uid = (userId && String(userId).trim()) || _currentUserId
  if (!uid) throw new Error('请先登录')
  const u = _users[uid]
  if (!u) throw new Error('用户不存在')
  const postCount = _posts.filter(
    p => p.authorId === uid && p.status === 'published' && p.category !== 'emotion',
  ).length
  const fileShareCount = _mockFileShares.filter(f => f.userId === uid && f.status === 'approved').length
  return {
    user: {
      _id: u._id,
      nickname: u.nickname,
      class: u.class || '',
      avatarUrl: u.avatarUrl || '',
      role: u.role,
      exp: u.exp || 0,
      score: u.score || 0,
      postCount,
      achievementCounts: u.achievementCounts || {},
    },
    fileShareCount,
    isMe: uid === _currentUserId,
  }
}

function _wallRowToClient(m) {
  return {
    _id: m._id,
    authorId: m.authorId,
    authorName: m.authorName,
    isAdmin: m.isAdmin,
    content: m.content,
    createdAt: m.createdAt,
  }
}

export async function mockWallList(userId, page = 1, pageSize = 30) {
  await delay()
  const oid = (userId && String(userId).trim()) || ''
  if (!oid) return { messages: [], total: 0, hasMore: false }
  let rows = _wallMessages.filter(m => m.profileOwnerId === oid)
  rows = [...rows].sort((a, b) => {
    if (a.isAdmin !== b.isAdmin) return a.isAdmin ? -1 : 1
    return new Date(b.createdAt) - new Date(a.createdAt)
  })
  const total = rows.length
  const start = (page - 1) * pageSize
  const slice = rows.slice(start, start + pageSize).map(_wallRowToClient)
  return { messages: slice, total, hasMore: start + pageSize < total }
}

export async function mockWallAdd(userId, content) {
  await delay()
  const u = cur()
  if (!u) throw new Error('请先登录')
  const owner = (userId && String(userId).trim()) || ''
  if (!owner) throw new Error('参数不完整')
  const text = (content || '').trim()
  if (!text) throw new Error('留言不能为空')
  if (text.length > 500) throw new Error('留言过长')
  if (!sensitiveCheck(text).pass) throw new Error('留言包含不适宜内容')
  if (!_users[owner]) throw new Error('用户不存在')
  const row = {
    _id: genId(),
    profileOwnerId: owner,
    authorId: u._id,
    authorName: (u.nickname || '用户').slice(0, 64),
    isAdmin: u.role === 'admin',
    content: text,
    createdAt: now(),
  }
  _wallMessages.push(row)
  return {}
}

export async function mockWallDelete(messageId) {
  await delay()
  const viewer = cur()
  if (!viewer) throw new Error('请先登录')
  const mid = String(messageId)
  const idx = _wallMessages.findIndex(m => String(m._id) === mid)
  if (idx < 0) throw new Error('留言不存在')
  const msg = _wallMessages[idx]
  if (viewer.role === 'admin') {
    _wallMessages.splice(idx, 1)
    return {}
  }
  if (viewer._id === msg.profileOwnerId) {
    if (msg.isAdmin) throw new Error('无法删除导生留言')
    _wallMessages.splice(idx, 1)
    return {}
  }
  throw new Error('无权删除')
}

function _fileShareToClient(f) {
  const author = _users[f.userId]
  return {
    _id: f._id,
    userId: f.userId,
    title: f.title,
    description: f.description || '',
    fileUrl: f.fileUrl,
    fileName: f.fileName || '',
    status: f.status,
    likeCount: f.likeCount || 0,
    likedByMe: _fileShareLikes.has(`${_currentUserId}:${f._id}`),
    authorName: author ? author.nickname : '未知',
    authorAvatarUrl: author?.avatarUrl || '',
    createdAt: f.createdAt,
  }
}

export async function mockGetFileShareList(params = {}) {
  await delay()
  const page = Math.max(parseInt(params.page, 10) || 1, 1)
  const pageSize = Math.min(Math.max(parseInt(params.pageSize, 10) || 20, 5), 50)
  const myFiles = params.myFiles
  let list = _mockFileShares.filter((f) => {
    if (myFiles) return f.userId === _currentUserId
    return f.status === 'approved'
  })
  list = [...list].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  const total = list.length
  const start = (page - 1) * pageSize
  const slice = list.slice(start, start + pageSize).map(_fileShareToClient)
  return { items: slice, total, hasMore: start + pageSize < total }
}

export async function mockFileShareLike(fileShareId) {
  await delay()
  const fs = _mockFileShares.find(f => String(f._id) === String(fileShareId))
  if (!fs) throw new Error('文件不存在')
  if (fs.status !== 'approved') throw new Error('仅已通过的分享可点赞')
  if (!_currentUserId) throw new Error('请先登录')
  if (fs.userId === _currentUserId) throw new Error('不能给自己的分享点赞')
  const key = `${_currentUserId}:${fs._id}`
  if (_fileShareLikes.has(key)) {
    return { likeCount: fs.likeCount || 0, likedByMe: true }
  }
  _fileShareLikes.add(key)
  fs.likeCount = (fs.likeCount || 0) + 1
  const owner = _users[fs.userId]
  if (owner) {
    owner.score = (owner.score || 0) + 10
    _pointsLog.unshift({
      _id: genId(),
      userId: owner._id,
      delta: 10,
      type: 'score',
      reason: 'file_like_received',
      relatedId: String(fs._id),
      createdAt: now(),
    })
  }
  return { likeCount: fs.likeCount, likedByMe: true }
}

// ========== Admin ==========

export async function mockAdminGetReports() {
  await delay()
  const admin = cur()
  const base = _posts.filter(p => {
    if (p.category === 'emotion') return false
    if (isMockSuperAdmin(admin)) return true
    const ac = _adminClass()
    return _authorClass(p.authorId) === ac && SCHOOL_CLASSES.includes(ac)
  })
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
  if (!_mockAdminActsOnAuthor(post.authorId)) throw new Error('无权操作其他班级的帖子')
  post.status = action
  post.updatedAt = now()
  const au = _users[post.authorId]
  _pushAdminLog('post_override', 'post', postId, {
    newStatus: action,
    summary: (post.content || '').slice(0, 120),
    authorNickname: au ? au.nickname : '',
    authorClass: au ? au.class : _authorClass(post.authorId),
  })
  return {}
}

export async function mockAdminPinPost(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) return {}
  if (!_mockAdminActsOnAuthor(post.authorId)) throw new Error('无权操作')
  post.pinned = true
  post.updatedAt = now()
  return {}
}

export async function mockAdminUnpinPost(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) return {}
  if (!_mockAdminActsOnAuthor(post.authorId)) throw new Error('无权操作')
  post.pinned = false
  post.updatedAt = now()
  return {}
}

export async function mockPostLike(postId) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) throw new Error('帖子不存在')
  if (post.category === 'emotion') throw new Error('该类型帖子不支持点赞')
  const key = `${_currentUserId}:${postId}`
  if (_postLikes.has(key)) {
    return { likeCount: post.likeCount || 0, likedByMe: true }
  }
  _postLikes.add(key)
  post.likeCount = (post.likeCount || 0) + 1
  post.updatedAt = now()
  return { likeCount: post.likeCount, likedByMe: true }
}

export async function mockAdminPostFeatured(postId, featured) {
  await delay()
  const post = _posts.find(p => p._id === postId)
  if (!post) throw new Error('帖子不存在')
  if (!_mockAdminActsOnAuthor(post.authorId)) throw new Error('无权操作')
  if (post.category === 'emotion') throw new Error('情感倾诉不可设为优质帖')
  const want = !!featured
  post.featured = want
  if (want && post.status === 'flagged') {
    post.status = 'published'
    post.flagged = false
    post.flaggedWords = []
    post.flaggedCategories = []
    post.flaggedHighlighted = ''
  } else if (want && (post.status === 'pending' || post.status === 'review')) {
    post.status = 'published'
  }
  post.updatedAt = now()
  return { featured: want }
}

export async function mockAdminGetPendingAchievements() {
  await delay()
  const admin = cur()
  if (isMockSuperAdmin(admin)) {
    return { achievements: _achievements.filter(a => a.status === 'pending') }
  }
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
  if (!_mockAdminActsOnAuthor(ach.userId)) throw new Error('无权审核其他班级的成果')
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
    authorClass: user ? user.class : _authorClass(ach.userId),
    expGain: ach.expAwarded,
  })
  return { expGain: ach.expAwarded }
}

export async function mockAdminRejectAchievement(id) {
  await delay()
  const ach = _achievements.find(a => a._id === id)
  if (!ach) return {}
  if (!_mockAdminActsOnAuthor(ach.userId)) throw new Error('无权审核其他班级的成果')
  ach.status = 'rejected'
  const user = _users[ach.userId]
  _pushAdminLog('achievement_reject', 'achievement', id, {
    title: ach.title,
    authorNickname: user ? user.nickname : '',
    authorClass: user ? user.class : _authorClass(ach.userId),
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
  const admin = cur()
  if (!isMockSuperAdmin(admin) && !_mockAdminActsOnAuthor(userId)) {
    throw new Error('仅可操作本班用户')
  }
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

export async function mockAdminSuperPromoteUser(targetUserId) {
  await delay()
  const admin = cur()
  if (!admin || !isMockSuperAdmin(admin)) throw new Error('仅最高管理员可指定导生')
  const u = _users[targetUserId]
  if (!u) throw new Error('用户不存在')
  u.role = 'admin'
  u.updatedAt = now()
  return { user: safeUser(u) }
}

export async function mockAdminGetEmotionPosts() {
  await delay()
  const admin = cur()
  if (isMockSuperAdmin(admin)) {
    return { posts: _posts.filter(p => p.category === 'emotion') }
  }
  const ac = _adminClass()
  return {
    posts: _posts.filter(
      p => p.category === 'emotion' && _authorClass(p.authorId) === ac && SCHOOL_CLASSES.includes(ac)
    ),
  }
}

export async function mockAdminGetEmotionHistory() {
  await delay()
  const admin = cur()
  const aid = _currentUserId
  const inClassEmotion = (p) => {
    if (p.category !== 'emotion') return false
    if (isMockSuperAdmin(admin)) return true
    const ac = _adminClass()
    return _authorClass(p.authorId) === ac && SCHOOL_CLASSES.includes(ac)
  }
  return {
    posts: _posts.filter(p => {
      if (!inClassEmotion(p)) return false
      return _comments.some(
        c => c.postId === p._id && c.authorId === aid && c.isAdmin
      )
    }),
  }
}

export async function mockAdminGetReviewHistory() {
  await delay()
  const ac = _adminClass()
  if (!SCHOOL_CLASSES.includes(ac)) return { logs: [] }
  const logs = _adminLogs.filter(l => (l.detail && l.detail.authorClass) === ac)
  return { logs }
}

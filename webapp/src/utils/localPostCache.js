/**
 * 本地持久化：用户读过的帖子详情 + 广场首屏快照（按用户隔离）
 * 先读本地再请求网络，失败时保留已展示的缓存。
 */

const PREFIX_READ = 'yunji_read_v2_'
const PREFIX_FEED = 'yunji_feed_v2_'
const MAX_READ_ENTRIES = 100
const MAX_JSON_CHARS = 1_200_000

function getUserId() {
  try {
    const u = JSON.parse(localStorage.getItem('userInfo') || '{}')
    return String(u._id || 'anon')
  } catch {
    return 'anon'
  }
}

function readStoreKey() {
  return PREFIX_READ + getUserId()
}

function loadReadStore() {
  try {
    const raw = localStorage.getItem(readStoreKey())
    if (!raw) return { order: [], items: {} }
    const o = JSON.parse(raw)
    return {
      order: Array.isArray(o.order) ? o.order : [],
      items: o.items && typeof o.items === 'object' ? o.items : {},
    }
  } catch {
    return { order: [], items: {} }
  }
}

function persistReadStore(store) {
  while (store.order.length > MAX_READ_ENTRIES) {
    const id = store.order.pop()
    if (id) delete store.items[id]
  }
  let json = JSON.stringify(store)
  while (json.length > MAX_JSON_CHARS && store.order.length > 8) {
    const id = store.order.pop()
    if (id) delete store.items[id]
    json = JSON.stringify(store)
  }
  try {
    localStorage.setItem(readStoreKey(), json)
  } catch {
    while (store.order.length > 20) {
      const id = store.order.pop()
      if (id) delete store.items[id]
    }
    try {
      localStorage.setItem(readStoreKey(), JSON.stringify(store))
    } catch { /* 仍超配额则放弃 */ }
  }
}

/** 缓存用户打开过的帖子（正文 + 评论列表） */
export function cacheReadPost(post, comments) {
  if (!post || post._id == null) return
  const id = String(post._id)
  const store = loadReadStore()
  store.order = store.order.filter((x) => x !== id)
  store.order.unshift(id)
  try {
    store.items[id] = {
      post: JSON.parse(JSON.stringify(post)),
      comments: JSON.parse(JSON.stringify(comments || [])),
      readAt: Date.now(),
    }
  } catch {
    return
  }
  persistReadStore(store)
}

export function getCachedReadPost(postId) {
  const store = loadReadStore()
  const id = String(postId)
  const row = store.items[id]
  if (!row || !row.post) return null
  return row
}

export function invalidateReadPost(postId) {
  const id = String(postId)
  const store = loadReadStore()
  store.order = store.order.filter((x) => x !== id)
  delete store.items[id]
  persistReadStore(store)
}

function feedKey(category, keyword, pageSize) {
  const cat = category || 'all'
  const kw = (keyword || '').trim()
  return `${PREFIX_FEED}${getUserId()}_${encodeURIComponent(`${cat}|${kw}|${pageSize}`)}`
}

/** 广场首屏快照（仅第一页，与分类/搜索/分页大小绑定） */
export function getFeedSnapshot(category, keyword, pageSize) {
  try {
    const raw = localStorage.getItem(feedKey(category, keyword, pageSize))
    if (!raw) return null
    const o = JSON.parse(raw)
    if (!Array.isArray(o.posts)) return null
    return { posts: o.posts, hasMore: !!o.hasMore, savedAt: o.savedAt || 0 }
  } catch {
    return null
  }
}

export function saveFeedSnapshot(category, keyword, pageSize, posts, hasMore) {
  try {
    const payload = {
      posts: JSON.parse(JSON.stringify(posts || [])),
      hasMore: !!hasMore,
      savedAt: Date.now(),
    }
    localStorage.setItem(feedKey(category, keyword, pageSize), JSON.stringify(payload))
  } catch { /* quota */ }
}

/** 登出前调用：清除当前用户在本地与帖子相关的缓存 */
export function clearUserLocalPostCaches() {
  const uid = getUserId()
  try {
    localStorage.removeItem(readStoreKey())
    const toRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i)
      if (k && k.startsWith(`${PREFIX_FEED}${uid}_`)) toRemove.push(k)
    }
    toRemove.forEach((k) => localStorage.removeItem(k))
  } catch { /* ignore */ }
}

/** 从已保存的广场快照中移除某帖（删帖后避免列表里仍出现） */
export function removePostFromAllFeedSnapshots(postId) {
  const uid = getUserId()
  const prefix = `${PREFIX_FEED}${uid}_`
  const id = String(postId)
  try {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const k = localStorage.key(i)
      if (!k || !k.startsWith(prefix)) continue
      try {
        const raw = localStorage.getItem(k)
        if (!raw) continue
        const o = JSON.parse(raw)
        if (!Array.isArray(o.posts)) continue
        const next = o.posts.filter((p) => String(p._id) !== id)
        if (next.length !== o.posts.length) {
          localStorage.setItem(k, JSON.stringify({ ...o, posts: next }))
        }
      } catch { /* ignore */ }
    }
  } catch { /* ignore */ }
}

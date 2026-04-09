/**
 * 列表/网格使用缩略图参数 ?thumb=feed；详情大图与下载使用 originalImageUrl。
 */
const THUMB_KEY = 'thumb'
const THUMB_VAL = 'feed'

function isLikelyLocalMedia(url) {
  if (!url) return false
  const s = String(url)
  if (/^data:|^blob:/i.test(s)) return false
  if (s.startsWith('/media/')) return true
  if (/^https?:\/\//i.test(s)) {
    try {
      const u = new URL(s)
      return u.pathname.startsWith('/media/')
    } catch {
      return false
    }
  }
  return false
}

function isGifUrl(url) {
  return /\.gif(\?|#|$)/i.test(String(url || ''))
}

/** 广场卡片、详情页九宫格：可带缩略图参数（GIF 除外） */
export function withFeedThumb(url) {
  if (!url || !isLikelyLocalMedia(url) || isGifUrl(url)) return url
  const s = String(url)
  const q = s.indexOf('?')
  const path = q >= 0 ? s.slice(0, q) : s
  const query = q >= 0 ? s.slice(q + 1) : ''
  const params = new URLSearchParams(query)
  params.set(THUMB_KEY, THUMB_VAL)
  return `${path}?${params.toString()}`
}

/** 原图 URL（预览、下载） */
export function originalImageUrl(url) {
  if (!url) return ''
  const s = String(url)
  const q = s.indexOf('?')
  if (q < 0) return s
  const path = s.slice(0, q)
  const params = new URLSearchParams(s.slice(q + 1))
  params.delete(THUMB_KEY)
  const rest = params.toString()
  return rest ? `${path}?${rest}` : path
}

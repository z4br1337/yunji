<template>
  <div
    class="post-card"
    :class="{
      'post-boutique': post.boutique,
      'post-highlight': !post.boutique && (post.pinned || post.featured),
      'post-flagged': post.status === 'flagged',
    }"
    @click="$emit('click', post)"
  >
    <div v-if="post.pinned || post.featured || post.boutique" class="post-corner-badges">
      <span
        v-if="post.pinned"
        class="corner-badge"
        title="置顶帖：在广场列表优先展示"
      >📌 置顶</span>
      <span
        v-if="post.featured"
        class="corner-badge corner-badge-featured"
        title="优质帖：导生标记的优质内容"
      >⭐ 优质</span>
      <span
        v-if="post.boutique"
        class="corner-badge corner-badge-boutique"
        title="精品帖：点赞数超过30自动展示"
      >💎 精品</span>
    </div>
    <div class="post-header">
      <div class="avatar avatar-sm" :class="{ clickable: !post.isAnonymous }" @click.stop="onAvatarClick">
        <img v-if="!post.isAnonymous && post.authorAvatarUrl" :src="post.authorAvatarUrl" alt="" />
        <span v-else>{{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}</span>
      </div>
      <div class="post-meta">
        <span class="post-author">{{ post.visibleAuthorName || '匿名用户' }}</span>
        <span v-if="post.status === 'flagged'" class="flag-badge">⚠️ 违规</span>
      </div>
      <span class="post-time text-xs text-muted">{{ formatTime(post.createdAt) }}</span>
    </div>
    <div class="post-body">
      <div v-if="post.topics && post.topics.length" class="post-topics">
        <button
          v-for="t in post.topics"
          :key="t"
          type="button"
          class="topic-hash"
          @click.stop="goTopic(t)"
        >#{{ t }}#</button>
      </div>
      <p v-if="post.status === 'flagged' && isAdmin" class="flagged-content" v-html="post.flaggedHighlighted || post.content"></p>
      <p v-else class="post-content">{{ post.content }}</p>
      <div
        v-if="post.images && post.images.length"
        class="post-media-grid"
        :class="'count-' + Math.min(post.images.length, 9)"
      >
        <div
          v-for="(img, i) in post.images.slice(0, 9)"
          :key="i"
          class="post-media-cell"
        >
          <img
            :src="thumbSrc(img)"
            alt=""
            loading="lazy"
            decoding="async"
            :fetchpriority="i === 0 ? 'high' : 'low'"
          />
        </div>
      </div>
    </div>
    <div class="post-footer">
      <span class="category-tag" v-if="categoryLabel">{{ categoryLabel }}</span>
      <span class="status-tag" v-if="post.status !== 'published'" :class="'status-' + post.status">
        {{ statusLabel }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { POST_CATEGORIES, POST_STATUS_LABELS } from '../utils/config.js'
import { withFeedThumb } from '../utils/imageUrl.js'

const props = defineProps({
  post: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false }
})
const emit = defineEmits(['click', 'avatar-click'])
const router = useRouter()

const catMap = {}
POST_CATEGORIES.forEach(c => { catMap[c.key] = c.label })
catMap['daily'] = '日常分享'
catMap['experience'] = '经验分享'
catMap['achievement'] = '成果分享'
catMap['emotion'] = '情感倾诉'

const categoryLabel = computed(() => catMap[props.post.category] || '')
const statusLabel = computed(() => POST_STATUS_LABELS[props.post.status] || props.post.status)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function onAvatarClick() {
  if (props.post.isAnonymous) return
  emit('avatar-click', props.post)
}

function goTopic(t) {
  const name = String(t || '').trim()
  if (!name) return
  router.push({ path: '/feed', query: { topic: name } })
}

function thumbSrc(url) {
  return withFeedThumb(url)
}
</script>

<style scoped>
.post-card {
  position: relative;
  background: rgba(255,255,255,0.98);
  border-radius: 20px;
  padding: 16px;
  border: 1px solid rgba(17,24,39,0.06);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  margin-bottom: 12px;
  box-shadow: 0 8px 22px rgba(17,24,39,0.04);
  overflow: hidden;
}
.post-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(255,130,0,0.75), transparent);
  opacity: 0;
  transform: translateY(-1px);
  transition: opacity 0.2s ease;
}
.post-card:hover {
  transform: translateY(-1px);
  border-color: rgba(255,130,0,0.18);
  box-shadow: 0 12px 30px rgba(17,24,39,0.07);
}
.post-card:hover::before { opacity: 1; }
.post-boutique {
  background: linear-gradient(180deg, #fffef9, #fffdfa);
  border-left: 3px solid var(--primary);
}
.post-boutique .post-author,
.post-boutique .post-content,
.post-boutique .post-time { color: var(--text-primary); }
.post-boutique .topic-hash { background: rgba(255,130,0,0.08); color: var(--primary); }
.post-highlight { border-left: 3px solid var(--warning); background: linear-gradient(180deg, #fffdf6, #fffaf0); }
.post-flagged { border-left: 3px solid var(--danger); background: #fff8f8; }
.post-corner-badges { position: absolute; top: 10px; right: 12px; z-index: 1; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; pointer-events: none; }
.corner-badge {
  font-size: 0.65rem;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(255,130,0,0.10);
  color: var(--primary);
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 4px 10px rgba(255,130,0,0.06);
}
.corner-badge-boutique { background: rgba(255,130,0,0.12); }
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-right: 72px; }
.post-meta { flex: 1; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-width: 0; }
.post-author { font-weight: 700; font-size: 0.93rem; }
.flag-badge { font-size: 0.7rem; padding: 1px 6px; border-radius: 999px; background: rgba(255,77,79,0.12); color: var(--danger); }
.post-time { white-space: nowrap; flex-shrink: 0; }
.post-body { margin-bottom: 10px; }
.post-topics { margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px 8px; }
.topic-hash {
  border: 1px solid rgba(255,130,0,0.16);
  background: rgba(255,130,0,0.06);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--primary);
  cursor: pointer;
  font-family: inherit;
}
.topic-hash:hover { background: rgba(255,130,0,0.12); }
.post-content { font-size: 0.92rem; line-height: 1.68; word-break: break-word; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; color: var(--text-primary); }
.flagged-content { font-size: 0.92rem; line-height: 1.65; }
.post-media-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 10px; max-width: 100%; }
.post-media-grid.count-1 { grid-template-columns: 1fr; max-width: 240px; }
.post-media-grid.count-2 { grid-template-columns: repeat(2, 1fr); max-width: 360px; }
.post-media-cell { aspect-ratio: 1; border-radius: 10px; overflow: hidden; background: linear-gradient(180deg, #f4f6f8, #eceff3); }
.post-media-cell img { width: 100%; height: 100%; object-fit: cover; display: block; }
.post-footer { display: flex; align-items: center; gap: 8px; padding-top: 2px; }
.category-tag { font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; background: rgba(255,130,0,0.08); color: var(--primary); }
.status-tag { font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; }
.status-pending { background: rgba(245,165,36,0.12); color: var(--warning); }
.status-archived { background: #f1f3f5; color: #666; }
.status-flagged { background: rgba(255,77,79,0.12); color: var(--danger); }
.status-review { background: rgba(47,128,237,0.12); color: var(--info); }
.clickable { cursor: pointer; }
.clickable:hover { opacity: 0.85; }
@media (max-width: 480px) {
  .post-card { padding: 14px; border-radius: 18px; }
  .post-header { padding-right: 62px; }
  .post-author { font-size: 0.9rem; }
  .post-content { -webkit-line-clamp: 5; }
}
</style>

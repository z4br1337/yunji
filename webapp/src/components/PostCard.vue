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
      <p v-if="post.status === 'flagged' && isAdmin" class="flagged-content" v-html="post.flaggedHighlighted || post.content"></p>
      <p v-else class="post-content">{{ post.content }}</p>
      <div v-if="post.images && post.images.length" class="post-images">
        <img
          v-for="(img, i) in post.images.slice(0, 3)"
          :key="i"
          :src="img"
          class="post-img"
          loading="lazy"
          decoding="async"
          :fetchpriority="i === 0 ? 'high' : 'low'"
        />
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
import { POST_CATEGORIES, POST_STATUS_LABELS } from '../utils/config.js'

const props = defineProps({
  post: { type: Object, required: true },
  isAdmin: { type: Boolean, default: false }
})
const emit = defineEmits(['click', 'avatar-click'])

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
</script>

<style scoped>
.post-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: var(--transition);
  margin-bottom: 12px;
}
.post-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-1px); }
.post-boutique {
  background: linear-gradient(165deg, #3d7dcc 0%, #5a9fe6 38%, #e8f2fc 72%, #ffffff 100%);
  border-left: 3px solid #2563b8;
  box-shadow: 0 4px 20px rgba(37, 99, 184, 0.12);
}
.post-boutique .post-author,
.post-boutique .post-content,
.post-boutique .post-time { color: var(--text-primary); }
.post-highlight { border-left: 3px solid var(--warning); background: #FFFDF5; }
.post-flagged { border-left: 3px solid var(--danger); background: #FFF5F5; }
.post-corner-badges {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  pointer-events: none;
}
.corner-badge {
  font-size: 0.65rem;
  padding: 2px 7px;
  border-radius: 4px;
  background: #FFF3CD;
  color: #856404;
  font-weight: 600;
  white-space: nowrap;
}
.corner-badge-featured { background: #FFF3CD; color: #856404; }
.corner-badge-boutique {
  background: rgba(255, 255, 255, 0.92);
  color: #1e4d8c;
  border: 1px solid rgba(30, 77, 140, 0.35);
}
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding-right: 72px; }
.post-meta { flex: 1; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; min-width: 0; }
.post-author { font-weight: 600; font-size: 0.9rem; }
.flag-badge { font-size: 0.7rem; padding: 1px 6px; border-radius: 4px; background: #F8D7DA; color: #721C24; }
.post-time { white-space: nowrap; flex-shrink: 0; }
.post-body { margin-bottom: 10px; }
.post-content { font-size: 0.9rem; line-height: 1.6; word-break: break-word; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.flagged-content { font-size: 0.9rem; line-height: 1.6; }
.post-images { display: flex; gap: 8px; margin-top: 10px; }
.post-img { width: 80px; height: 80px; object-fit: cover; border-radius: var(--radius-sm); }
.post-footer { display: flex; align-items: center; gap: 8px; }
.category-tag { font-size: 0.7rem; padding: 2px 8px; border-radius: 100px; background: rgba(74,144,217,0.1); color: var(--primary); }
.status-tag { font-size: 0.7rem; padding: 2px 8px; border-radius: 100px; }
.status-pending { background: #FFF3CD; color: #856404; }
.status-archived { background: #F0F0F0; color: #666; }
.status-flagged { background: #F8D7DA; color: #721C24; }
.status-review { background: #D1ECF1; color: #0C5460; }
.clickable { cursor: pointer; }
.clickable:hover { opacity: 0.8; }
</style>

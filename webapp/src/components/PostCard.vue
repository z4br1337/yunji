<template>
  <div class="post-card" :class="{ 'post-pinned': post.pinned, 'post-flagged': post.status === 'flagged' }" @click="$emit('click', post)">
    <div class="post-header">
      <div class="avatar avatar-sm" :class="{ clickable: !post.isAnonymous }" @click.stop="onAvatarClick">
        {{ post.isAnonymous ? '匿' : (post.visibleAuthorName || '?')[0] }}
      </div>
      <div class="post-meta">
        <span class="post-author">{{ post.visibleAuthorName || '匿名用户' }}</span>
        <span v-if="post.pinned" class="pin-badge">📌 置顶</span>
        <span v-if="post.status === 'flagged'" class="flag-badge">⚠️ 违规</span>
      </div>
      <span class="post-time text-xs text-muted">{{ formatTime(post.createdAt) }}</span>
    </div>
    <div class="post-body">
      <p v-if="post.status === 'flagged' && isAdmin" class="flagged-content" v-html="post.flaggedHighlighted || post.content"></p>
      <p v-else class="post-content">{{ post.content }}</p>
      <div v-if="post.images && post.images.length" class="post-images">
        <img v-for="(img, i) in post.images.slice(0, 3)" :key="i" :src="img" class="post-img" />
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
</script>

<style scoped>
.post-card { background: var(--bg-card); border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow); cursor: pointer; transition: var(--transition); margin-bottom: 12px; }
.post-card:hover { box-shadow: var(--shadow-lg); transform: translateY(-1px); }
.post-pinned { border-left: 3px solid var(--warning); background: #FFFDF5; }
.post-flagged { border-left: 3px solid var(--danger); background: #FFF5F5; }
.post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.post-meta { flex: 1; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.post-author { font-weight: 600; font-size: 0.9rem; }
.pin-badge, .flag-badge { font-size: 0.7rem; padding: 1px 6px; border-radius: 4px; }
.pin-badge { background: #FFF3CD; color: #856404; }
.flag-badge { background: #F8D7DA; color: #721C24; }
.post-time { white-space: nowrap; }
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

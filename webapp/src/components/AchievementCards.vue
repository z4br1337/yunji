<template>
  <div>
    <div v-for="ach in items" :key="ach._id" class="ach-card card mb-8" :class="'ach-' + ach.status">
      <div class="flex justify-between items-center mb-4">
        <span class="font-bold">{{ ach.title }}</span>
        <span class="badge" :class="statusClass(ach.status)">{{ statusLabel(ach.status) }}</span>
      </div>
      <p v-if="mode === 'community' && (ach.authorNickname || ach.authorClass)" class="text-xs text-muted mb-4">
        {{ ach.authorNickname || '用户' }}<template v-if="ach.authorClass"> · {{ ach.authorClass }}</template>
      </p>
      <p class="text-sm text-secondary">{{ ach.description }}</p>
      <div class="flex gap-8 mt-8 items-center flex-wrap">
        <span class="text-xs text-muted">蜕变等级: {{ ach.level }}</span>
        <span v-if="ach.expAwarded" class="text-xs text-muted">| 经验值: +{{ ach.expAwarded }}</span>
        <span class="text-xs text-muted">| {{ categoryLabel(ach.category) }}</span>
      </div>
      <div v-if="ach.images && ach.images.length" class="ach-images mt-8">
        <img v-for="(img, i) in ach.images" :key="i" :src="img" class="ach-img" alt="" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ACHIEVEMENT_CATEGORIES, POST_STATUS_LABELS } from '../utils/config.js'

defineProps({
  items: { type: Array, default: () => [] },
  mode: { type: String, default: 'mine' },
})

const catMap = {}
ACHIEVEMENT_CATEGORIES.forEach((c) => { catMap[c.key] = c.label })
function categoryLabel(key) { return catMap[key] || key }

function statusLabel(s) { return POST_STATUS_LABELS[s] || s }
function statusClass(s) {
  if (s === 'approved') return 'badge-success'
  if (s === 'pending') return 'badge-warning'
  if (s === 'rejected') return 'badge-danger'
  return 'badge-primary'
}
</script>

<style scoped>
.ach-card.ach-pending { border-left: 3px solid var(--warning); }
.ach-card.ach-rejected { border-left: 3px solid var(--danger); }
.ach-images { display: flex; gap: 8px; flex-wrap: wrap; }
.ach-img { width: 60px; height: 60px; object-fit: cover; border-radius: var(--radius-sm); }
</style>

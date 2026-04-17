<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center" :class="{ 'mb-8': embedded }">
      <h2 v-if="!embedded">闪光时刻</h2>
      <span v-else></span>
      <button class="btn btn-primary btn-sm" @click="$router.push('/achievement/create')">+ 提交闪光时刻</button>
    </div>

    <!-- Five Virtue Stats -->
    <div class="virtue-grid mb-16">
      <div v-for="cat in achCategories" :key="cat.key" class="virtue-card" :style="{ borderColor: cat.color }">
        <span class="virtue-icon">{{ cat.icon }}</span>
        <span class="virtue-label">{{ cat.label }}</span>
        <span class="virtue-count">{{ achCounts[cat.key] || 0 }}</span>
      </div>
    </div>

    <!-- 广场 / 我的 -->
    <div class="chip-group mb-16">
      <button class="chip" :class="{ active: feedMode === 'community' }" @click="feedMode = 'community'">闪光广场</button>
      <button class="chip" :class="{ active: feedMode === 'mine' }" @click="feedMode = 'mine'">我的</button>
    </div>

    <FiveVirtueRadar
      v-if="showRadar"
      :scores="radarScores"
      class="radar-block"
    />

    <!-- 分类 -->
    <div class="chip-group mb-16">
      <button class="chip" :class="{ active: filterCat === '' }" @click="filterCat = ''">全部</button>
      <button v-for="cat in achCategories" :key="cat.key" class="chip" :class="{ active: filterCat === cat.key }" @click="filterCat = cat.key">{{ cat.label }}</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="achievements.length">
      <div v-for="ach in achievements" :key="ach._id" class="ach-card card mb-8" :class="'ach-' + ach.status">
        <div class="flex justify-between items-center mb-4">
          <span class="font-bold">{{ ach.title }}</span>
          <span class="badge" :class="statusClass(ach.status)">{{ statusLabel(ach.status) }}</span>
        </div>
        <p v-if="feedMode === 'community' && (ach.authorNickname || ach.authorClass)" class="text-xs text-muted mb-4">
          {{ ach.authorNickname || '用户' }}<template v-if="ach.authorClass"> · {{ ach.authorClass }}</template>
        </p>
        <p class="text-sm text-secondary">{{ ach.description }}</p>
        <div class="flex gap-8 mt-8 items-center">
          <span class="text-xs text-muted">蜕变等级: {{ ach.level }}</span>
          <span class="text-xs text-muted" v-if="ach.expAwarded">| 经验值: +{{ ach.expAwarded }}</span>
          <span class="text-xs text-muted">| {{ categoryLabel(ach.category) }}</span>
        </div>
        <div v-if="ach.images && ach.images.length" class="ach-images mt-8">
          <img v-for="(img, i) in ach.images" :key="i" :src="img" class="ach-img" />
        </div>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">🌟</div>
      <div class="text">还没有闪光时刻，快去提交吧！</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, inject } from 'vue'
import { useUserStore } from '../stores/user.js'
import { ACHIEVEMENT_CATEGORIES, POST_STATUS_LABELS } from '../utils/config.js'
import { scoresFromApprovedAchievements } from '../utils/achievementRadar.js'
import * as api from '../api/index.js'
import FiveVirtueRadar from '../components/FiveVirtueRadar.vue'

defineProps({ embedded: { type: Boolean, default: false } })

const { state, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const achCategories = ACHIEVEMENT_CATEGORIES
const achCounts = computed(() => state.userInfo?.achievementCounts || {})
const achievements = ref([])
/** 「我的」下全部分类原始列表，用于雷达图与前端筛选 */
const mineAchievementsRaw = ref([])
const filterCat = ref('')
const feedMode = ref('community')
const loading = ref(false)

const showRadar = computed(() => feedMode.value === 'mine' && filterCat.value === '')

const radarScores = computed(() => scoresFromApprovedAchievements(mineAchievementsRaw.value))

function statusLabel(s) { return POST_STATUS_LABELS[s] || s }
function statusClass(s) {
  if (s === 'approved') return 'badge-success'
  if (s === 'pending') return 'badge-warning'
  if (s === 'rejected') return 'badge-danger'
  return 'badge-primary'
}

const catMap = {}
ACHIEVEMENT_CATEGORIES.forEach(c => { catMap[c.key] = c.label })
function categoryLabel(key) { return catMap[key] || key }

async function loadData() {
  loading.value = true
  try {
    if (feedMode.value === 'community') {
      mineAchievementsRaw.value = []
      const params = { community: true }
      if (filterCat.value) params.category = filterCat.value
      const result = await api.getAchievements(params)
      achievements.value = result.achievements || []
    } else {
      const result = await api.getAchievements({})
      mineAchievementsRaw.value = result.achievements || []
      let list = mineAchievementsRaw.value
      if (filterCat.value) list = list.filter((a) => a.category === filterCat.value)
      achievements.value = list
      try {
        await refreshProfile()
      } catch { /* 静默 */ }
    }
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

watch([feedMode, filterCat], () => {
  loadData()
})

onMounted(() => {
  loadData()
})

onActivated(() => {
  loadData()
})
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.virtue-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.virtue-card { background: var(--bg-card); border-radius: var(--radius-sm); padding: 12px 8px; text-align: center; border-bottom: 3px solid; box-shadow: var(--shadow); }
.virtue-icon { font-size: 1.3rem; display: block; }
.virtue-label { font-size: 0.75rem; color: var(--text-secondary); display: block; }
.virtue-count { font-size: 1.1rem; font-weight: 700; display: block; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 14px; border-radius: 100px; font-size: 0.85rem; background: #F0F2F5; border: 1px solid transparent; color: var(--text-secondary); transition: var(--transition); }
.chip.active { background: var(--primary); color: #fff; }
.ach-card.ach-pending { border-left: 3px solid var(--warning); }
.ach-card.ach-rejected { border-left: 3px solid var(--danger); }
.ach-images { display: flex; gap: 8px; flex-wrap: wrap; }
.ach-img { width: 60px; height: 60px; object-fit: cover; border-radius: var(--radius-sm); }

.radar-block { margin-bottom: 16px; }

@media (max-width: 480px) {
  .virtue-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>

<template>
  <div v-if="viewingOther" class="page-container">
    <div class="page-header flex justify-between items-center mb-12">
      <h2>闪光时刻</h2>
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>
    <GrowthBookEmbed embedded :target-user-id="otherUserId" />
  </div>

  <div v-else class="page-container gb-page">
    <div class="page-header flex justify-between items-center mb-12">
      <h2>闪光时刻</h2>
      <button type="button" class="btn btn-primary btn-sm" @click="$router.push('/achievement/create')">
        + 提交闪光时刻
      </button>
    </div>

    <div class="gb-main-tabs" role="tablist">
      <button
        type="button"
        class="gb-main-tab"
        :class="{ active: mainTab === 'plaza' }"
        @click="setMainTab('plaza')"
      >闪光广场</button>
      <button
        type="button"
        class="gb-main-tab"
        :class="{ active: mainTab === 'handbook' }"
        @click="setMainTab('handbook')"
      >成长手册</button>
    </div>

    <div class="virtue-grid mb-16">
      <div v-for="cat in achCategories" :key="cat.key" class="virtue-card" :style="{ borderColor: cat.color }">
        <span class="virtue-icon">{{ cat.icon }}</span>
        <span class="virtue-label">{{ cat.label }}</span>
        <span class="virtue-count">{{ achCounts[cat.key] || 0 }}</span>
      </div>
    </div>

    <template v-if="mainTab === 'plaza'">
      <div class="chip-group mb-16">
        <button class="chip" :class="{ active: plazaFilter === '' }" @click="plazaFilter = ''">全部</button>
        <button
          v-for="cat in achCategories"
          :key="cat.key"
          class="chip"
          :class="{ active: plazaFilter === cat.key }"
          @click="plazaFilter = cat.key"
        >{{ cat.label }}</button>
      </div>
      <div v-if="plazaLoading" class="loading-spinner"><div class="spinner"></div></div>
      <AchievementCards v-else-if="plazaList.length" :items="plazaList" mode="community" />
      <div v-else class="empty-state">
        <div class="icon">🌟</div>
        <div class="text">广场暂无闪光时刻</div>
      </div>
    </template>

    <template v-else>
      <div v-if="bookLoading" class="loading-spinner mb-16"><div class="spinner"></div></div>
      <template v-else-if="bookData">
        <div class="card mb-16">
          <div class="flex items-center gap-12 mb-8">
            <div class="avatar avatar-lg">{{ (bookData.user.nickname || '?')[0] }}</div>
            <div>
              <h3 class="mb-0">{{ bookData.user.nickname }}</h3>
              <p class="text-sm text-secondary">{{ bookData.user.class }}</p>
              <span class="badge badge-primary mt-4">Lv{{ bookLevel.level }} {{ bookLevel.title }}</span>
            </div>
          </div>
          <div v-if="bookData.isOwner" class="flex justify-between items-center mt-12">
            <span class="text-sm">公开成长手册</span>
            <input type="checkbox" class="toggle" :checked="bookData.growthBookPublic" @change="togglePublic" />
          </div>
        </div>

        <!-- 五育雷达 + 三维坐标：数据分别来自五育分类与「三维发展」闪光时刻；后续新增时刻类型时可扩展 achievementRadar 与独立可视化组件 -->
        <div v-if="showRadar" class="card radar-block radar-visual-card">
          <ThreeAxesGrowth :scores="growth3dScores" />
          <FiveVirtueRadar compact :scores="radarScores" />
        </div>

        <div class="chip-group mb-16">
          <button class="chip" :class="{ active: mineFilter === '' }" @click="mineFilter = ''">全部</button>
          <button
            v-for="cat in achCategories"
            :key="cat.key"
            class="chip"
            :class="{ active: mineFilter === cat.key }"
            @click="mineFilter = cat.key"
          >{{ cat.label }}</button>
        </div>

        <div v-if="mineLoading" class="loading-spinner"><div class="spinner"></div></div>
        <AchievementCards v-else-if="filteredMine.length" :items="filteredMine" mode="mine" />
        <div v-else class="empty-state">
          <div class="icon">🌟</div>
          <div class="text">还没有闪光时刻，快去提交吧！</div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onActivated, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { ACHIEVEMENT_CATEGORIES } from '../utils/config.js'
import { scoresFromApprovedAchievements, scoresFromApprovedGrowthAchievements } from '../utils/achievementRadar.js'
import { getLevelInfo } from '../utils/level.js'
import * as api from '../api/index.js'
import FiveVirtueRadar from '../components/FiveVirtueRadar.vue'
import ThreeAxesGrowth from '../components/ThreeAxesGrowth.vue'
import GrowthBookEmbed from './GrowthBook.vue'
import AchievementCards from '../components/AchievementCards.vue'

const route = useRoute()
const router = useRouter()
const { state, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const achCategories = ACHIEVEMENT_CATEGORIES
const achCounts = computed(() => state.userInfo?.achievementCounts || {})

const otherUserId = computed(() => {
  const q = route.query.userId
  return q != null && String(q).trim() !== '' ? String(q).trim() : ''
})
const meId = computed(() => state.userInfo?._id || '')
const viewingOther = computed(() => !!otherUserId.value && otherUserId.value !== meId.value)

const mainTab = ref(route.query.tab === 'handbook' ? 'handbook' : 'plaza')
const plazaFilter = ref('')
const mineFilter = ref('')

const plazaList = ref([])
const plazaLoading = ref(false)
const mineRaw = ref([])
const mineLoading = ref(false)
const bookData = ref(null)
const bookLoading = ref(false)

const bookLevel = computed(() => getLevelInfo(bookData.value?.user?.exp))
const showRadar = computed(() => mainTab.value === 'handbook' && mineFilter.value === '')
const radarScores = computed(() => scoresFromApprovedAchievements(mineRaw.value))
/** 仅统计「三维发展」维度（academic / practice / inner）已审核通过项 */
const growth3dScores = computed(() => scoresFromApprovedGrowthAchievements(mineRaw.value))

const filteredMine = computed(() => {
  let list = mineRaw.value
  if (mineFilter.value) list = list.filter((a) => a.category === mineFilter.value)
  return list
})

function setMainTab(tab) {
  mainTab.value = tab
  router.replace({ path: '/growth-book', query: { tab } })
}

async function loadPlaza() {
  plazaLoading.value = true
  try {
    const params = { community: true }
    if (plazaFilter.value) params.category = plazaFilter.value
    const r = await api.getAchievements(params)
    plazaList.value = r.achievements || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    plazaLoading.value = false
  }
}

async function loadHandbook() {
  bookLoading.value = true
  mineLoading.value = true
  try {
    const [book, mine] = await Promise.all([
      api.getGrowthBook(),
      api.getAchievements({}),
    ])
    bookData.value = book
    mineRaw.value = mine.achievements || []
    try {
      await refreshProfile()
    } catch { /* ignore */ }
  } catch (e) {
    showToast(e.message || '加载失败')
    bookData.value = null
    mineRaw.value = []
  } finally {
    bookLoading.value = false
    mineLoading.value = false
  }
}

async function togglePublic(e) {
  const val = e.target.checked
  try {
    await api.setGrowthBookPublic(val)
    if (bookData.value) bookData.value.growthBookPublic = val
    showToast(val ? '已公开成长手册' : '已设为私密')
  } catch {
    showToast('操作失败')
    e.target.checked = !val
  }
}

watch(
  () => route.query.tab,
  () => {
    if (viewingOther.value) return
    const t = route.query.tab
    mainTab.value = t === 'handbook' ? 'handbook' : 'plaza'
  },
)

watch(plazaFilter, () => {
  if (viewingOther.value || mainTab.value !== 'plaza') return
  loadPlaza()
})

watch(mainTab, (t) => {
  if (viewingOther.value) return
  if (t === 'handbook') loadHandbook()
  else loadPlaza()
}, { immediate: true })

onActivated(() => {
  if (viewingOther.value) return
  if (mainTab.value === 'plaza') loadPlaza()
  else loadHandbook()
})
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.gb-main-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--bg);
}
.gb-main-tab {
  flex: 1;
  padding: 14px 16px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition);
}
.gb-main-tab.active {
  background: #fff;
  color: var(--primary);
  box-shadow: var(--shadow);
}
.gb-main-tab:hover:not(.active) {
  color: var(--text-primary);
}
.virtue-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.virtue-card { background: var(--bg-card); border-radius: var(--radius-sm); padding: 12px 8px; text-align: center; border-bottom: 3px solid; box-shadow: var(--shadow); }
.virtue-icon { font-size: 1.3rem; display: block; }
.virtue-label { font-size: 0.75rem; color: var(--text-secondary); display: block; }
.virtue-count { font-size: 1.1rem; font-weight: 700; display: block; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 14px; border-radius: 100px; font-size: 0.85rem; background: #F0F2F5; border: 1px solid transparent; color: var(--text-secondary); transition: var(--transition); }
.chip.active { background: var(--primary); color: #fff; }
.radar-block { margin-bottom: 16px; }
.radar-visual-card { padding: 0; overflow: hidden; }
.radar-visual-card :deep(.radar-wrap--compact) { border-radius: 0; }
.toggle { width: 44px; height: 24px; appearance: none; background: #ccc; border-radius: 12px; position: relative; cursor: pointer; transition: var(--transition); }
.toggle:checked { background: var(--primary); }
.toggle::after { content: ''; position: absolute; width: 20px; height: 20px; background: #fff; border-radius: 50%; top: 2px; left: 2px; transition: var(--transition); }
.toggle:checked::after { left: 22px; }

@media (max-width: 480px) {
  .virtue-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>

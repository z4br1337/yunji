<template>
  <div class="page-container" :class="{ 'growth-embedded': embedded }">
    <div v-if="!embedded" class="page-header flex justify-between items-center">
      <h2>成长手册</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="bookData">
      <!-- User Summary -->
      <div class="card mb-16">
        <div class="flex items-center gap-12 mb-8">
          <div class="avatar avatar-lg">{{ (bookData.user.nickname || '?')[0] }}</div>
          <div>
            <h3>{{ bookData.user.nickname }}</h3>
            <p class="text-sm text-secondary">{{ bookData.user.class }}</p>
            <div class="flex gap-8 mt-4">
              <span class="badge badge-primary">Lv{{ levelInfo.level }} {{ levelInfo.title }}</span>
            </div>
          </div>
        </div>

        <!-- Virtue Stats -->
        <div class="virtue-mini-grid mt-8">
          <div v-for="cat in achCategories" :key="cat.key" class="virtue-mini" :style="{ color: cat.color }">
            <span>{{ cat.icon }} {{ cat.label }}</span>
            <span class="font-bold">{{ (bookData.user.achievementCounts || {})[cat.key] || 0 }}</span>
          </div>
        </div>

        <!-- Privacy toggle (owner only) -->
        <div v-if="bookData.isOwner" class="flex justify-between items-center mt-16">
          <span class="text-sm">公开成长手册</span>
          <input type="checkbox" class="toggle" :checked="bookData.growthBookPublic" @change="togglePublic" />
        </div>
      </div>

      <!-- Achievement List -->
      <h3 class="mb-8">闪光时刻</h3>
      <template v-if="bookData.achievements.length">
        <div v-for="ach in filteredAchs" :key="ach._id" class="card mb-8">
          <div class="flex justify-between items-center mb-4">
            <span class="font-bold">{{ ach.title }}</span>
            <span class="text-xs text-muted">等级 {{ ach.level }}</span>
          </div>
          <p class="text-sm text-secondary">{{ ach.description }}</p>
          <div v-if="ach.images && ach.images.length" class="flex gap-8 mt-8">
            <img v-for="(img, i) in ach.images" :key="i" :src="img" style="width:60px;height:60px;object-fit:cover;border-radius:8px" />
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        <div class="icon">📖</div>
        <div class="text">暂无审核通过的闪光时刻</div>
      </div>
    </template>
    <div v-else class="empty-state">
      <div class="icon">🔒</div>
      <div class="text">{{ errorMsg || '无法查看' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { ACHIEVEMENT_CATEGORIES } from '../utils/config.js'
import { getLevelInfo } from '../utils/level.js'
import * as api from '../api/index.js'

defineProps({
  embedded: { type: Boolean, default: false },
})

const route = useRoute()
const showToast = inject('showToast')

const achCategories = ACHIEVEMENT_CATEGORIES
const bookData = ref(null)
const loading = ref(true)
const errorMsg = ref('')
const filterCat = ref('')

const levelInfo = computed(() => getLevelInfo(bookData.value?.user?.exp))
const filteredAchs = computed(() => {
  if (!bookData.value) return []
  if (!filterCat.value) return bookData.value.achievements
  return bookData.value.achievements.filter(a => a.category === filterCat.value)
})

async function loadData() {
  loading.value = true
  try {
    const userId = route.query.userId || undefined
    bookData.value = await api.getGrowthBook(userId)
  } catch (e) {
    errorMsg.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function togglePublic(e) {
  const val = e.target.checked
  try {
    await api.setGrowthBookPublic(val)
    bookData.value.growthBookPublic = val
    showToast(val ? '已公开成长手册' : '已设为私密')
  } catch { showToast('操作失败') }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-container.growth-embedded { padding-top: 0; }
.page-header { margin-bottom: 16px; }
.virtue-mini-grid { display: flex; flex-wrap: wrap; gap: 12px; }
.virtue-mini { display: flex; gap: 6px; align-items: center; font-size: 0.85rem; }
.toggle { width: 44px; height: 24px; appearance: none; background: #ccc; border-radius: 12px; position: relative; cursor: pointer; transition: var(--transition); }
.toggle:checked { background: var(--primary); }
.toggle::after { content: ''; position: absolute; width: 20px; height: 20px; background: #fff; border-radius: 50%; top: 2px; left: 2px; transition: var(--transition); }
.toggle:checked::after { left: 22px; }
</style>

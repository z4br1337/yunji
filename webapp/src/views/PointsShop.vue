<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>萤火积分兑换商店</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div class="my-score card mb-16">
      <span class="text-secondary">我的积分</span>
      <span class="score-num">{{ userScore }}</span>
    </div>

    <h4 class="mb-8">消耗萤火积分</h4>
    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <div v-else class="shop-grid">
      <div v-for="item in items" :key="item._id" class="shop-card card">
        <div class="shop-img-wrap">
          <img v-if="item.imageUrl" :src="item.imageUrl" :alt="item.title" />
          <div v-else class="shop-placeholder">📦</div>
        </div>
        <h4 class="shop-title">{{ item.title }}</h4>
        <p class="shop-subtitle">消耗萤火积分</p>
        <div class="shop-price">{{ item.price }}</div>
        <button class="btn btn-ghost btn-sm shop-btn" :disabled="item.stock <= 0 || userScore < item.price"
          @click="exchange(item)">
          {{ item.stock <= 0 ? '已售罄' : item.price > userScore ? '积分不足' : '兑换' }}
        </button>
        <p class="shop-stock">剩余数量 {{ item.stock }}</p>
      </div>
    </div>

    <h4 class="mb-8 mt-24">我的兑换记录</h4>
    <div v-if="myRecords.length" class="card">
      <div v-for="r in myRecords" :key="r._id" class="record-item flex justify-between">
        <span>{{ r.itemTitle }}</span>
        <span class="text-muted">-{{ r.price }} 积分 · {{ formatTime(r.createdAt) }}</span>
      </div>
    </div>
    <div v-else class="empty-state">
      <div class="icon">📋</div>
      <div class="text">暂无兑换记录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'

const showToast = inject('showToast')
const { state, refreshProfile } = useUserStore()
const userScore = ref(state.userInfo?.score || 0)
const items = ref([])
const myRecords = ref([])
const loading = ref(false)

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadItems() {
  loading.value = true
  try {
    const [shopRes, recordsRes] = await Promise.all([
      api.getShopItems(),
      api.getMyExchanges()
    ])
    items.value = shopRes.items || []
    myRecords.value = recordsRes.records || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function exchange(item) {
  if (item.stock <= 0 || userScore.value < item.price) return
  try {
    const res = await api.shopExchange(item.itemKey)
    await refreshProfile()
    userScore.value = res?.score ?? state.userInfo?.score ?? 0
    showToast('兑换成功')
    loadItems()
  } catch (e) {
    showToast(e.message || '兑换失败')
  }
}

onMounted(() => {
  userScore.value = state.userInfo?.score || 0
  loadItems()
})
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.my-score { display: flex; align-items: center; justify-content: space-between; padding: 16px; }
.score-num { font-size: 1.5rem; font-weight: 700; color: var(--primary); }
.shop-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.shop-card { text-align: center; padding: 16px; }
.shop-img-wrap { width: 100%; aspect-ratio: 1; background: var(--bg); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 12px; }
.shop-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.shop-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 3rem; }
.shop-title { font-size: 0.95rem; margin-bottom: 4px; }
.shop-subtitle { font-size: 0.75rem; color: var(--text-muted); margin-bottom: 8px; }
.shop-price { font-size: 1.4rem; font-weight: 700; color: var(--primary); margin-bottom: 8px; }
.shop-btn { width: 100%; }
.shop-stock { font-size: 0.75rem; color: var(--text-muted); margin-top: 8px; }
.record-item { padding: 12px 0; border-bottom: 1px solid var(--border); }
.record-item:last-child { border-bottom: none; }
</style>

<template>
  <div class="activity-list-page">
    <div class="page-toolbar flex items-center gap-12 mb-8">
      <button type="button" class="btn btn-ghost btn-sm" @click="router.push('/feed')">← 返回</button>
    </div>
    <header class="list-header">
      <h1 class="list-title">近期活动</h1>
    </header>
    <div class="header-rule" />

    <div v-if="loading" class="loading-wrap">
      <div class="loading-spinner"><div class="spinner"></div></div>
    </div>

    <div v-else-if="!campaigns.length" class="empty-card card text-center text-muted p-24">
      暂无近期活动，敬请期待
    </div>

    <ul v-else class="activity-card-list">
      <li v-for="c in campaigns" :key="c._id">
        <button type="button" class="activity-name-card" @click="goColumn(c._id)">
          <span class="card-title">{{ c.title }}</span>
          <span v-if="c.isActive" class="card-badge">展示中</span>
          <span class="card-arrow" aria-hidden="true">›</span>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const loading = ref(true)
const campaigns = ref([])

async function load() {
  loading.value = true
  try {
    const r = await api.listPublicActivityCampaigns()
    campaigns.value = Array.isArray(r.campaigns) ? r.campaigns : []
  } catch (e) {
    showToast(e.message || '加载失败')
    campaigns.value = []
  } finally {
    loading.value = false
  }
}

function goColumn(campaignId) {
  router.push({ name: 'RecentActivity', params: { campaignId: String(campaignId) } })
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.activity-list-page {
  max-width: 680px;
  margin: 0 auto;
  padding: 16px 16px 24px;
  min-height: 60vh;
}
.list-header {
  padding-bottom: 12px;
}
.list-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: var(--text-primary);
}
.header-rule {
  height: 1px;
  background: var(--border);
  margin-bottom: 20px;
}
.loading-wrap {
  padding: 48px 0;
  display: flex;
  justify-content: center;
}
.activity-card-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.activity-name-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  min-height: 64px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  box-shadow: var(--shadow);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: var(--transition);
}
.activity-name-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-lg);
}
.card-title {
  flex: 1;
  min-width: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
}
.card-badge {
  flex-shrink: 0;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(74, 144, 217, 0.14);
  color: var(--primary);
}
.card-arrow {
  flex-shrink: 0;
  font-size: 1.25rem;
  color: var(--text-muted);
  opacity: 0.85;
}
.empty-card {
  border: 1px solid var(--border);
  margin-top: 8px;
}
</style>

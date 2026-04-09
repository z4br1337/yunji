<template>
  <div class="search-page page-container">
    <div class="search-header flex items-center gap-8">
      <button type="button" class="btn btn-ghost btn-sm back-btn" aria-label="返回" @click="$router.back()">←</button>
      <input
        v-model.trim="keyword"
        class="form-input search-field"
        type="search"
        placeholder="搜索帖子关键词…"
        enterkeyhint="search"
        @keyup.enter="runSearch"
      />
      <button type="button" class="btn btn-primary btn-sm search-submit" @click="runSearch">搜索</button>
    </div>

    <h3 class="section-title">热门话题</h3>
    <p class="section-hint text-xs text-muted">按帖子使用次数排序（不展示具体数字）</p>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <ul v-else class="hot-list">
      <li
        v-for="(t, i) in hotTopics"
        :key="t"
        class="hot-row flex items-center"
        @click="goTopic(t)"
      >
        <span class="rank" :class="rankClass(i + 1)">{{ i + 1 }}</span>
        <span class="hot-topic-name">#{{ t }}#</span>
      </li>
    </ul>
    <div v-if="!loading && !hotTopics.length" class="empty-hint text-muted text-sm">暂无话题数据，去发帖添加话题吧</div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const keyword = ref('')
const hotTopics = ref([])
const loading = ref(true)

function rankClass(n) {
  if (n === 1) return 'rank-gold'
  if (n === 2) return 'rank-silver'
  if (n === 3) return 'rank-bronze'
  return ''
}

function runSearch() {
  const q = keyword.value.trim()
  router.push({ path: '/feed', query: q ? { q } : {} })
}

function goTopic(t) {
  router.push({ path: '/feed', query: { topic: t } })
}

onMounted(async () => {
  loading.value = true
  try {
    const r = await api.getHotTopics()
    hotTopics.value = r.topics || []
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container { max-width: 640px; margin: 0 auto; padding: 16px; }
.search-header {
  margin-bottom: 24px;
  padding: 8px 0;
}
.back-btn { flex-shrink: 0; padding: 8px 12px; font-size: 1.1rem; }
.search-field {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  font-size: 0.95rem;
}
.search-submit { flex-shrink: 0; border-radius: 20px; padding: 8px 16px; }
.section-title {
  font-size: 1.05rem;
  margin: 8px 0 4px;
  font-weight: 700;
}
.section-hint { margin-bottom: 12px; }
.hot-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}
.hot-row {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
  gap: 14px;
}
.hot-row:last-child { border-bottom: none; }
.hot-row:hover { background: var(--bg); }
.rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
  background: #eef1f5;
  color: var(--text-muted);
}
.rank-gold { background: linear-gradient(145deg, #ffd54f, #ffb300); color: #5d4200; }
.rank-silver { background: linear-gradient(145deg, #e0e0e0, #bdbdbd); color: #424242; }
.rank-bronze { background: linear-gradient(145deg, #ffcc80, #ef6c00); color: #4e2500; }
.hot-topic-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}
.empty-hint { padding: 24px; text-align: center; }
</style>

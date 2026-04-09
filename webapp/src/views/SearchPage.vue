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

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else>
      <div class="hot-tabs flex" role="tablist" aria-label="热门切换">
        <button
          type="button"
          role="tab"
          class="hot-tab"
          :class="{ active: hotTab === 'topics' }"
          :aria-selected="hotTab === 'topics'"
          @click="hotTab = 'topics'"
        >热门话题</button>
        <button
          type="button"
          role="tab"
          class="hot-tab"
          :class="{ active: hotTab === 'posts' }"
          :aria-selected="hotTab === 'posts'"
          @click="hotTab = 'posts'"
        >热门帖子</button>
      </div>

      <template v-if="hotTab === 'topics'">
        <ul class="hot-list">
          <li
            v-for="(t, i) in hotTopics"
            :key="'t-' + t"
            class="hot-row flex items-center"
            @click="goTopic(t)"
          >
            <span class="rank" :class="rankClass(i + 1)">{{ i + 1 }}</span>
            <span class="hot-topic-name">#{{ t }}#</span>
          </li>
        </ul>
        <div v-if="!hotTopics.length" class="empty-hint text-muted text-sm">暂无话题数据，去发帖添加话题吧</div>
      </template>

      <template v-else>
        <ul v-if="hotPosts.length" class="hot-list">
          <li
            v-for="(row, i) in hotPosts"
            :key="'p-' + row._id"
            class="hot-row flex items-center"
            @click="goPost(row._id)"
          >
            <span class="rank" :class="rankClass(i + 1)">{{ i + 1 }}</span>
            <span class="hot-post-snippet">{{ row.snippet }}</span>
          </li>
        </ul>
        <div v-else class="empty-hint text-muted text-sm">暂无热门帖子</div>
      </template>
    </template>
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
const hotPosts = ref([])
const hotTab = ref('topics')
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

function goPost(id) {
  if (!id) return
  router.push(`/post/${id}`)
}

onMounted(async () => {
  loading.value = true
  try {
    const [r, hp] = await Promise.all([api.getHotTopics(), api.getHotPostSnippets()])
    hotTopics.value = (r.topics || []).slice(0, 20)
    hotPosts.value = (hp.posts || []).slice(0, 20)
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
.hot-tabs {
  margin: 8px 0 14px;
  padding: 4px;
  border-radius: 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  gap: 6px;
}
.hot-tab {
  flex: 1;
  border: none;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  color: var(--text-secondary);
  font-family: inherit;
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
}
.hot-tab:hover {
  color: var(--primary);
  background: rgba(74, 144, 217, 0.08);
}
.hot-tab.active {
  background: var(--bg-card);
  color: var(--primary);
  box-shadow: var(--shadow);
}
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
.hot-topic-name,
.hot-post-snippet {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 0;
  flex: 1;
  line-height: 1.35;
}
.hot-post-snippet {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.empty-hint { padding: 24px; text-align: center; }
</style>

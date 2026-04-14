<template>
  <div class="activity-page page-container">
    <div class="page-toolbar flex items-center gap-12 mb-12">
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">← 返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>

    <template v-else-if="!campaign">
      <div class="empty-card card text-center text-muted p-24">
        {{ campaignId ? '未找到该活动，可能已被删除' : '暂无近期活动，敬请期待' }}
      </div>
    </template>

    <template v-else>
      <header
        class="activity-hero"
        :style="heroStyle"
      >
        <div class="activity-hero-overlay">
          <h1 class="activity-title">{{ campaign.title }}</h1>
          <p class="activity-intro">{{ campaign.intro || '（暂无简介）' }}</p>
          <p class="activity-tag-hint text-sm">参与方式：发帖时在话题中添加 <strong>#{{ campaign.tag }}#</strong></p>
        </div>
      </header>

      <div class="section-divider" />

      <h2 class="related-title">相关帖子</h2>

      <div v-if="postsLoading" class="loading-spinner sm"><div class="spinner"></div></div>
      <template v-else-if="posts.length">
        <PostCard
          v-for="p in posts"
          :key="p._id"
          :post="p"
          :is-admin="isAdmin"
          @click="goDetail(p._id)"
          @avatar-click="onAvatarClick"
        />
      </template>
      <div v-else class="empty-related card text-muted text-sm text-center p-20">
        还没有带此话题的帖子，去广场发一条吧
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'
import PostCard from '../components/PostCard.vue'

const router = useRouter()
const route = useRoute()
const { state } = useUserStore()
const showToast = inject('showToast')

const loading = ref(true)
const postsLoading = ref(false)
const campaign = ref(null)
const posts = ref([])

const campaignId = computed(() => String(route.params.campaignId || '').trim())

const isAdmin = computed(() => state.isAdmin)

function bgUrlForCss(url) {
  if (!url) return ''
  const s = String(url)
  if (/^https?:\/\//i.test(s)) return s
  if (s.startsWith('/')) return `${window.location.origin}${s}`
  return s
}

const heroStyle = computed(() => {
  const u = campaign.value?.backgroundUrl
  if (u && String(u).trim()) {
    return {
      backgroundImage: `linear-gradient(to top, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.25) 45%, transparent 72%), url(${bgUrlForCss(u)})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  return {
    background: 'linear-gradient(145deg, #3d6fa8 0%, #5a9fe6 40%, #8ec5fc 100%)',
  }
})

async function loadCampaign() {
  loading.value = true
  try {
    const id = campaignId.value
    if (!id) {
      campaign.value = null
      return
    }
    const r = await api.getActivityCampaignById(id)
    campaign.value = r.campaign || null
  } catch (e) {
    showToast(e.message || '加载失败')
    campaign.value = null
  } finally {
    loading.value = false
  }
}

async function loadPosts() {
  const c = campaign.value
  if (!c?.tag) {
    posts.value = []
    return
  }
  postsLoading.value = true
  try {
    const r = await api.getPosts({
      page: 1,
      pageSize: 30,
      excludeEmotion: true,
      topic: c.tag,
    })
    posts.value = r.posts || []
  } catch (e) {
    showToast(e.message || '帖子加载失败')
    posts.value = []
  } finally {
    postsLoading.value = false
  }
}

function goDetail(id) {
  router.push(`/post/${id}`)
}

function onAvatarClick(post) {
  if (post.isAnonymous) {
    showToast('该用户匿名发布')
    return
  }
  router.push({ name: 'PersonalHome', params: { userId: post.authorId } })
}

async function reloadAll() {
  await loadCampaign()
  await loadPosts()
}

watch(campaignId, () => {
  reloadAll()
})

onMounted(() => {
  reloadAll()
})
</script>

<style scoped>
.page-container { max-width: 680px; margin: 0 auto; padding: 16px; }
.activity-hero {
  border-radius: var(--radius);
  overflow: hidden;
  min-height: 200px;
  margin-bottom: 0;
}
.activity-hero-overlay {
  min-height: 200px;
  padding: 28px 20px 22px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 10px;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
}
.activity-title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1.3;
}
.activity-intro {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.55;
  opacity: 0.96;
  white-space: pre-wrap;
  word-break: break-word;
}
.activity-tag-hint {
  margin: 4px 0 0;
  opacity: 0.92;
}
.activity-tag-hint strong { font-weight: 700; }
.section-divider {
  height: 1px;
  background: var(--border);
  margin: 20px 0 16px;
}
.related-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 12px;
}
.empty-card { border: 1px solid var(--border); }
.empty-related { border: 1px dashed var(--border); }
.loading-spinner.sm { padding: 16px; }
</style>

<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>用户详情</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div v-if="loading" class="loading-spinner"><div class="spinner"></div></div>
    <template v-else-if="userData">
      <div class="card mb-16">
        <div class="flex items-center gap-12 mb-8">
          <div class="avatar avatar-lg">
          <img v-if="userData.user.avatarUrl" :src="userData.user.avatarUrl" alt="" />
          <span v-else>{{ (userData.user.nickname || '?')[0] }}</span>
        </div>
          <div>
            <h3>{{ userData.user.nickname }}</h3>
            <p class="text-sm text-secondary">{{ userData.user.class }}</p>
            <p class="text-sm text-muted">学号：{{ userData.user.studentId || '未绑定' }}</p>
            <div class="flex gap-8 mt-4">
              <span class="badge badge-primary">{{ userData.user.role === 'admin' ? '导生' : '用户' }}</span>
              <span class="badge badge-success">Exp: {{ userData.user.exp || 0 }}</span>
            </div>
          </div>
        </div>
        <div class="flex gap-16 mt-8">
          <div class="text-center">
            <div class="font-bold">{{ userData.stats.postCount }}</div>
            <div class="text-xs text-muted">帖子</div>
          </div>
          <div class="text-center">
            <div class="font-bold">{{ userData.stats.achievementCount }}</div>
            <div class="text-xs text-muted">成果</div>
          </div>
        </div>
      </div>

      <!-- Score user -->
      <div class="card mb-16">
        <h4 class="mb-8">评分</h4>
        <div class="flex gap-8 items-center">
          <input class="form-input" type="number" v-model.number="scoreDelta" placeholder="分值" style="width:100px" />
          <input class="form-input" v-model="scoreReason" placeholder="原因" />
          <button class="btn btn-primary btn-sm" @click="doScore">评分</button>
        </div>
      </div>

      <!-- View Growth Book -->
      <button class="btn btn-ghost btn-block" @click="$router.push(`/growth-book?userId=${route.params.userId}`)">
        查看成长手册
      </button>

      <!-- Points Log -->
      <div class="card mt-16">
        <h4 class="mb-8">近期积分记录</h4>
        <div v-for="log in userData.recentPointsLog" :key="log._id" class="flex justify-between mb-4 text-sm">
          <span>{{ log.reason }}</span>
          <span :class="log.delta > 0 ? 'text-success' : 'text-danger'">{{ log.delta > 0 ? '+' : '' }}{{ log.delta }}</span>
        </div>
        <div v-if="!userData.recentPointsLog.length" class="text-muted text-sm">暂无记录</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import * as api from '../../api/index.js'

const route = useRoute()
const showToast = inject('showToast')

const userData = ref(null)
const loading = ref(true)
const scoreDelta = ref(10)
const scoreReason = ref('')

async function loadData() {
  loading.value = true
  try {
    userData.value = await api.adminGetUserProfile(route.params.userId)
  } catch (e) {
    showToast(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function doScore() {
  if (!scoreDelta.value) { showToast('请输入分值'); return }
  try {
    await api.adminScoreUser(route.params.userId, scoreDelta.value, scoreReason.value)
    showToast('评分成功')
    await loadData()
  } catch (e) {
    showToast(e.message || '评分失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.text-success { color: var(--success); }
.text-danger { color: var(--danger); }
</style>

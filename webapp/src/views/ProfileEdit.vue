<template>
  <div class="page-container">
    <div class="page-header">
      <h2>完善个人资料</h2>
      <p class="text-secondary text-sm">请填写以下必填信息后方可使用完整功能</p>
    </div>
    <div class="card">
      <div class="form-group">
        <label class="form-label">昵称 *</label>
        <input class="form-input" v-model="nickname" placeholder="请输入昵称" maxlength="20" />
      </div>
      <div class="form-group">
        <label class="form-label">班级 *</label>
        <input class="form-input" v-model="userClass" placeholder="例如：计科2301" maxlength="20" />
      </div>
      <button class="btn btn-primary btn-block mt-16" :disabled="saving" @click="handleSave">
        {{ saving ? '保存中...' : '保存并继续' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import * as api from '../api/index.js'

const router = useRouter()
const { state, refreshProfile } = useUserStore()
const showToast = inject('showToast')

const nickname = ref('')
const userClass = ref('')
const saving = ref(false)

onMounted(() => {
  if (state.userInfo) {
    nickname.value = state.userInfo.nickname || ''
    userClass.value = state.userInfo.class || ''
  }
})

async function handleSave() {
  if (!nickname.value.trim() || !userClass.value.trim()) {
    showToast('请填写所有必填项')
    return
  }
  saving.value = true
  try {
    await api.updateProfile({ nickname: nickname.value.trim(), class: userClass.value.trim() })
    await refreshProfile()
    showToast('资料保存成功')
    router.replace('/feed')
  } catch (e) {
    showToast(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 480px; margin: 0 auto; padding: 24px 16px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 1.4rem; }
</style>

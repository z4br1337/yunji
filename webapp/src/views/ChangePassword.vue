<template>
  <div class="page-container">
    <div class="page-header">
      <h2>修改密码</h2>
      <p class="text-muted text-sm">请输入旧密码并设置新密码</p>
    </div>

    <div class="card form-card">
      <div class="form-group">
        <label>旧密码</label>
        <input
          v-model.trim="form.oldPassword"
          class="form-input"
          type="password"
          placeholder="请输入旧密码"
          maxlength="64"
        />
      </div>

      <div class="form-group">
        <label>新密码</label>
        <input
          v-model.trim="form.newPassword"
          class="form-input"
          type="password"
          placeholder="请输入新密码（至少6位）"
          maxlength="64"
        />
      </div>

      <div class="form-group">
        <label>确认新密码</label>
        <input
          v-model.trim="form.confirmPassword"
          class="form-input"
          type="password"
          placeholder="请再次输入新密码"
          maxlength="64"
        />
      </div>

      <button class="btn btn-primary btn-block mt-8" :disabled="loading" @click="submit">
        {{ loading ? '提交中...' : '确认修改' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')
const loading = ref(false)
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

async function submit() {
  if (!form.oldPassword || !form.newPassword || !form.confirmPassword) {
    showToast('请完整填写密码信息')
    return
  }
  if (form.newPassword.length < 6) {
    showToast('新密码至少6位')
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    showToast('两次输入的新密码不一致')
    return
  }

  loading.value = true
  try {
    await api.changePassword(form.oldPassword, form.newPassword)
    showToast('密码修改成功，请重新登录')
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.replace('/login')
  } catch (e) {
    showToast(e.message || '修改失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 560px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.form-card { padding: 16px; }
.form-group { margin-bottom: 12px; }
label { display: block; margin-bottom: 6px; font-size: 0.9rem; color: var(--text-secondary); }
</style>

<template>
  <div class="page-container">
    <div class="card bind-card">
      <h2>绑定学号</h2>
      <p class="text-secondary text-sm mb-16">
        根据平台要求，使用云迹前须绑定学号。多个账号可以绑定同一学号；使用学号登录时，若存在多个账号将提示你选择要登录的账号。
      </p>
      <div class="form-group">
        <label class="form-label">学号</label>
        <input
          v-model.trim="studentId"
          class="form-input"
          type="text"
          maxlength="32"
          placeholder="4～32 位字母、数字、下划线或短横线"
          autocomplete="username"
          @keyup.enter="submit"
        />
      </div>
      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
      <button class="btn btn-primary btn-block" :disabled="loading" @click="submit">
        {{ loading ? '提交中…' : '确认绑定' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const showToast = inject('showToast')
const { refreshProfile, updateLocal } = useUserStore()

const studentId = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function submit() {
  errorMsg.value = ''
  const sid = studentId.value.trim()
  if (!sid) {
    errorMsg.value = '请输入学号'
    return
  }
  if (!/^[A-Za-z0-9_-]{4,32}$/.test(sid)) {
    errorMsg.value = '学号须为 4～32 位字母、数字、下划线或短横线'
    return
  }
  if (!window.confirm('确定绑定该学号吗？提交后不可自行修改，如需更换请联系管理员。')) return
  loading.value = true
  try {
    const data = await api.bindStudentId(sid)
    const u = data.user || data
    if (u) {
      updateLocal({
        studentId: u.studentId || sid,
        isSuperAdmin: u.isSuperAdmin,
      })
    }
    await refreshProfile()
    showToast('绑定成功')
    const user = JSON.parse(localStorage.getItem('userInfo') || '{}')
    await router.replace(user.profileCompleted ? '/feed' : '/profile-edit')
  } catch (e) {
    errorMsg.value = e.message || '绑定失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 24px 16px;
}
.bind-card {
  padding: 24px;
}
h2 {
  margin-bottom: 8px;
}
.error-text {
  color: var(--danger);
  font-size: 0.85rem;
  margin-bottom: 12px;
}
</style>

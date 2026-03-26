<template>
  <div class="login-page">
    <div class="bg-particles">
      <span v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)"></span>
    </div>

    <div class="login-card">
      <div class="login-logo">
        <img src="/yunji-logo.png" alt="云迹" class="logo-img" />
      </div>
      <h1 class="login-title">注册云迹</h1>
      <p class="login-subtitle">创建你的账号</p>

      <div class="form-group">
        <label class="form-label">昵称</label>
        <input class="form-input" v-model="nickname" placeholder="给自己取个名字（最多20字）" maxlength="20" />
      </div>
      <div class="form-group">
        <label class="form-label">账号</label>
        <input class="form-input" v-model="username" placeholder="设置登录账号（3~32位字母/数字）" maxlength="32" />
      </div>
      <div class="form-group">
        <label class="form-label">密码</label>
        <input class="form-input" type="password" v-model="password" placeholder="设置密码（至少6位）" @keyup.enter="focusConfirm" />
      </div>
      <div class="form-group">
        <label class="form-label">确认密码</label>
        <input class="form-input" ref="confirmInput" type="password" v-model="confirmPassword" placeholder="再次输入密码" @keyup.enter="handleRegister" />
      </div>

      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

      <button class="btn btn-primary btn-block" :disabled="submitting" @click="handleRegister">
        {{ submitting ? '注册中...' : '注册' }}
      </button>

      <p class="switch-text">
        已有账号？<router-link to="/login" class="link">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const { restoreSession } = useUserStore()
const showToast = inject('showToast')

const nickname = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)
const errorMsg = ref('')
const confirmInput = ref(null)

function focusConfirm() {
  confirmInput.value?.focus()
}

function particleStyle(i) {
  const size = 4 + Math.random() * 12
  const left = Math.random() * 100
  const delay = Math.random() * 15
  const duration = 8 + Math.random() * 12
  const opacity = 0.15 + Math.random() * 0.35
  return {
    width: size + 'px', height: size + 'px',
    left: left + '%',
    animationDelay: delay + 's',
    animationDuration: duration + 's',
    opacity
  }
}

async function handleRegister() {
  errorMsg.value = ''
  const nick = nickname.value.trim()
  const user = username.value.trim()
  const pwd = password.value
  const pwd2 = confirmPassword.value

  if (!nick) { errorMsg.value = '请输入昵称'; return }
  if (!user) { errorMsg.value = '请输入账号'; return }
  if (user.length < 3) { errorMsg.value = '账号长度至少 3 位'; return }
  if (!/^[a-zA-Z0-9_]+$/.test(user)) { errorMsg.value = '账号只能包含字母、数字和下划线'; return }
  if (!pwd) { errorMsg.value = '请输入密码'; return }
  if (pwd.length < 6) { errorMsg.value = '密码长度至少 6 位'; return }
  if (pwd !== pwd2) { errorMsg.value = '两次密码不一致'; return }

  submitting.value = true
  try {
    const data = await api.register(nick, user, pwd)
    const u = data.user || data
    if (u) {
      localStorage.setItem('userInfo', JSON.stringify(u))
    }
    restoreSession()
    showToast('注册成功，请先绑定学号')
    router.replace('/bind-student')
  } catch (e) {
    errorMsg.value = e.message || '注册失败'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  padding: 16px; position: relative; overflow: hidden;
  background: linear-gradient(-45deg, #e8d5b7, #f5e6d3, #d4e7d0, #c8dbe8, #e0cce8);
  background-size: 400% 400%;
  animation: bgShift 18s ease infinite;
}
@keyframes bgShift {
  0%   { background-position: 0% 50%; }
  25%  { background-position: 100% 50%; }
  50%  { background-position: 100% 100%; }
  75%  { background-position: 0% 100%; }
  100% { background-position: 0% 50%; }
}
.bg-particles { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.particle {
  position: absolute; bottom: -20px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.6); animation: floatUp linear infinite;
}
.particle:nth-child(odd) { background: rgba(168, 200, 140, 0.45); }
.particle:nth-child(3n) { background: rgba(210, 180, 140, 0.4); }
@keyframes floatUp {
  0%   { transform: translateY(0) scale(1); opacity: var(--o, 0.3); }
  50%  { opacity: var(--o, 0.3); }
  100% { transform: translateY(-110vh) scale(0.3); opacity: 0; }
}
.login-card {
  background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(16px);
  border-radius: var(--radius-lg); padding: 36px 32px;
  width: 100%; max-width: 400px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1), 0 0 0 1px rgba(255,255,255,0.6);
  text-align: center; position: relative; z-index: 1;
}
.login-logo { margin-bottom: 8px; display: flex; justify-content: center; }
.logo-img {
  width: 80px; height: 80px; object-fit: contain; border-radius: 50%;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.12));
  animation: logoBounce 3s ease-in-out infinite;
}
@keyframes logoBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.login-title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.login-subtitle { color: var(--text-secondary); margin-bottom: 24px; }
.error-text { color: var(--danger); font-size: 0.85rem; margin-bottom: 12px; }
.switch-text { margin-top: 16px; font-size: 0.85rem; color: var(--text-secondary); }
.link { color: var(--primary); font-weight: 600; }
.link:hover { text-decoration: underline; }
</style>

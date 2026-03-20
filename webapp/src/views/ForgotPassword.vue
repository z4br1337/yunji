<template>
  <div class="forgot-page" :class="{ 'forgot-page-simple': needSimpleMode }">
    <div class="bg-particles">
      <span v-for="i in particleCount" :key="i" class="particle" :class="{ 'particle-simple': needSimpleMode }" :style="particleStyle(i)"></span>
    </div>

    <div class="forgot-card" :class="{ 'forgot-card-simple': needSimpleMode }">
      <button type="button" class="back-link" @click="$router.push('/login')">‹ 返回登录</button>
      <h1 class="title">找回密码</h1>
      <p class="sub">通过已绑定的邮箱接收 5 位数字验证码</p>

      <!-- 步骤 1：邮箱 -->
      <template v-if="step === 1">
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model.trim="email"
            class="form-input"
            type="email"
            placeholder="请输入已绑定的邮箱"
            autocomplete="email"
            @keyup.enter="sendCode"
          />
        </div>
        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
        <button class="btn btn-primary btn-block" :disabled="loading || cooldown > 0" @click="sendCode">
          {{ cooldown > 0 ? `${cooldown}s 后可重发` : (loading ? '发送中...' : '发送验证码') }}
        </button>
      </template>

      <!-- 步骤 2：验证码 + 新密码 -->
      <template v-else>
        <p class="email-hint">验证码已发送至 <strong>{{ maskedEmail }}</strong></p>
        <div class="form-group">
          <label class="form-label">5 位验证码</label>
          <input
            v-model.trim="code"
            class="form-input"
            inputmode="numeric"
            maxlength="5"
            placeholder="请输入邮件中的验证码"
            @keyup.enter="submitReset"
          />
        </div>
        <div class="form-group">
          <label class="form-label">新密码</label>
          <input v-model="newPassword" class="form-input" type="password" placeholder="至少 6 位" @keyup.enter="submitReset" />
        </div>
        <div class="form-group">
          <label class="form-label">确认新密码</label>
          <input v-model="confirmPassword" class="form-input" type="password" placeholder="再次输入新密码" @keyup.enter="submitReset" />
        </div>
        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
        <button class="btn btn-primary btn-block" :disabled="loading" @click="submitReset">
          {{ loading ? '提交中...' : '重置密码并返回登录' }}
        </button>
        <button type="button" class="btn-text" @click="goStep1">更换邮箱</button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')
const isWindows = inject('isWindows', ref(false))
const isMobile = inject('isMobile', ref(false))
const needSimpleMode = computed(() => isWindows.value || isMobile.value)
const particleCount = computed(() => (needSimpleMode.value ? 4 : 20))

const step = ref(1)
const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMsg = ref('')
const cooldown = ref(0)
let cooldownTimer = null

const maskedEmail = computed(() => {
  const e = email.value.trim()
  const at = e.indexOf('@')
  if (at <= 1) return e
  return e[0] + '***' + e.slice(at)
})

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

function goStep1() {
  step.value = 1
  errorMsg.value = ''
  code.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
}

async function sendCode() {
  errorMsg.value = ''
  if (!email.value) {
    errorMsg.value = '请输入邮箱'
    return
  }
  loading.value = true
  try {
    await api.forgotPasswordSend(email.value)
    showToast('验证码已发送，请查收邮件')
    step.value = 2
    cooldown.value = 60
    if (cooldownTimer) clearInterval(cooldownTimer)
    cooldownTimer = setInterval(() => {
      cooldown.value -= 1
      if (cooldown.value <= 0) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
  } catch (e) {
    errorMsg.value = e.message || '发送失败'
  } finally {
    loading.value = false
  }
}

async function submitReset() {
  errorMsg.value = ''
  if (code.value.length !== 5 || !/^\d{5}$/.test(code.value)) {
    errorMsg.value = '请输入 5 位数字验证码'
    return
  }
  if (!newPassword.value || newPassword.value.length < 6) {
    errorMsg.value = '新密码至少 6 位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的新密码不一致'
    return
  }
  loading.value = true
  try {
    await api.forgotPasswordReset(email.value, code.value, newPassword.value)
    showToast('密码已重置，请使用新密码登录')
    await router.replace('/login')
  } catch (e) {
    errorMsg.value = e.message || '重置失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(-45deg, #e8d5b7, #f5e6d3, #d4e7d0, #c8dbe8, #e0cce8);
  background-size: 400% 400%;
  animation: bgShift 18s ease infinite;
}
.forgot-page-simple {
  animation: none;
  background: linear-gradient(135deg, #e8d5b7 0%, #d4e7d0 50%, #c8dbe8 100%);
}
@keyframes bgShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 100%; }
  100% { background-position: 0% 50%; }
}
.bg-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.particle {
  position: absolute;
  bottom: -20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  animation: floatUp linear infinite;
}
.particle-simple { animation-duration: 12s; }
@keyframes floatUp {
  0% { transform: translateY(0); opacity: var(--o, 0.3); }
  100% { transform: translateY(-110vh); opacity: 0; }
}

.forgot-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-lg);
  padding: 28px 24px 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  text-align: left;
}
.forgot-card-simple {
  backdrop-filter: none;
  background: #fff;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
}
.back-link {
  border: none;
  background: none;
  color: var(--primary);
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0;
  margin-bottom: 12px;
}
.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--text-primary);
}
.sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 24px;
}
.form-group { margin-bottom: 14px; }
.form-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 1rem;
  box-sizing: border-box;
}
.error-text {
  color: var(--danger);
  font-size: 0.85rem;
  margin: 0 0 12px;
}
.email-hint {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.5;
}
.btn-block { width: 100%; margin-top: 4px; }
.btn-text {
  display: block;
  width: 100%;
  margin-top: 14px;
  border: none;
  background: none;
  color: var(--primary);
  font-size: 0.85rem;
  cursor: pointer;
}
</style>

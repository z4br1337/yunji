<template>
  <div class="prefs-page">
    <header class="prefs-header">
      <button type="button" class="back-btn" @click="$router.push('/settings')" aria-label="返回">‹</button>
      <div class="header-text">
        <h1>设置</h1>
        <p class="sub">管理个人资料与账号安全</p>
      </div>
    </header>

    <nav class="tab-strip" role="tablist">
      <button
        type="button"
        role="tab"
        :aria-selected="tab === 'profile'"
        class="tab-pill"
        :class="{ active: tab === 'profile' }"
        @click="tab = 'profile'"
      >
        个人资料
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="tab === 'security'"
        class="tab-pill"
        :class="{ active: tab === 'security' }"
        @click="tab = 'security'"
      >
        账号安全
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="tab === 'student'"
        class="tab-pill"
        :class="{ active: tab === 'student' }"
        @click="tab = 'student'"
      >
        绑定学号
      </button>
    </nav>

    <!-- 个人资料 -->
    <div v-show="tab === 'profile'" class="panel card-elevated">
      <div class="panel-head">
        <span class="panel-icon">👤</span>
        <div>
          <h2>个人资料</h2>
          <p class="panel-desc">头像、昵称与班级</p>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">头像</label>
        <div class="avatar-section">
          <div class="avatar-preview" :class="{ 'has-avatar': selectedAvatar }">
            <img v-if="selectedAvatar" :src="selectedAvatar" alt="" />
            <span v-else>{{ (nickname || '?')[0] }}</span>
          </div>
          <div class="avatar-options">
            <p class="text-xs text-muted mb-8">预设头像或上传（≤700KB）</p>
            <div class="preset-grid">
              <button v-for="(url, i) in presetAvatars" :key="i" type="button"
                class="preset-btn" :class="{ active: selectedAvatar === url }"
                @click="selectPreset(url)">
                <img :src="url" alt="" />
              </button>
            </div>
            <div class="upload-row mt-8">
              <label class="btn btn-ghost btn-sm">
                <input type="file" accept="image/*" hidden @change="onAvatarUpload" />
                上传自定义头像
              </label>
              <span v-if="avatarError" class="text-danger text-xs">{{ avatarError }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">昵称 *</label>
        <input class="form-input input-soft" v-model="nickname" placeholder="请输入昵称" maxlength="20" />
      </div>
      <div class="form-group">
        <label class="form-label">班级 *</label>
        <select class="form-input form-select input-soft" v-model="userClass" required>
          <option value="" disabled>请选择班级</option>
          <option v-for="c in schoolClasses" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>
      <button class="btn btn-primary btn-block btn-save" :disabled="saving" @click="handleSaveProfile">
        {{ saving ? '保存中...' : '保存资料' }}
      </button>
    </div>

    <!-- 账号安全 -->
    <div v-show="tab === 'security'" class="panel card-elevated">
      <div class="panel-head">
        <span class="panel-icon">🔒</span>
        <div>
          <h2>修改密码</h2>
          <p class="panel-desc">验证旧密码后设置新密码</p>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">旧密码</label>
        <input v-model.trim="pwdForm.oldPassword" class="form-input input-soft" type="password" placeholder="请输入旧密码" maxlength="64" />
      </div>
      <div class="form-group">
        <label class="form-label">新密码</label>
        <input v-model.trim="pwdForm.newPassword" class="form-input input-soft" type="password" placeholder="至少 6 位" maxlength="64" />
      </div>
      <div class="form-group">
        <label class="form-label">确认新密码</label>
        <input v-model.trim="pwdForm.confirmPassword" class="form-input input-soft" type="password" placeholder="再次输入新密码" maxlength="64" />
      </div>
      <button class="btn btn-primary btn-block btn-save" :disabled="pwdLoading" @click="submitPassword">
        {{ pwdLoading ? '提交中...' : '确认修改密码' }}
      </button>
      <p class="hint text-xs text-muted mt-12">修改成功后需重新登录</p>
    </div>

    <!-- 绑定学号 -->
    <div v-show="tab === 'student'" class="panel card-elevated">
      <div class="panel-head">
        <span class="panel-icon">🎓</span>
        <div>
          <h2>绑定学号</h2>
          <p class="panel-desc">绑定后可使用学号登录；多个账号可绑定同一学号，学号登录时若有多个账号将提示选择（4～32 位字母、数字、下划线或短横线）</p>
        </div>
      </div>

      <template v-if="boundStudentId">
        <p class="bound-tip">当前已绑定学号：<strong>{{ boundStudentId }}</strong></p>
        <p class="text-xs text-muted">每个账号仅可绑定一次学号。如需更换请联系管理员。</p>
      </template>
      <template v-else>
        <div class="form-group">
          <label class="form-label">学号</label>
          <input
            v-model.trim="bindStudentInput"
            class="form-input input-soft"
            type="text"
            placeholder="请输入学号"
            autocomplete="username"
            maxlength="32"
          />
        </div>
        <p class="text-xs text-muted mb-12">请仔细核对学号；每个账号仅可绑定一次，提交后不可自行修改。</p>
        <button class="btn btn-primary btn-block btn-save" :disabled="bindStudentLoading" @click="submitBindStudent">
          {{ bindStudentLoading ? '提交中...' : '确认绑定学号' }}
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { SCHOOL_CLASSES } from '../utils/config.js'
import * as api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const { state, refreshProfile, logout } = useUserStore()
const showToast = inject('showToast')

const schoolClasses = SCHOOL_CLASSES
const tab = ref('profile')

const nickname = ref('')
const userClass = ref('')
const selectedAvatar = ref('')
const avatarError = ref('')
const saving = ref(false)
const presetAvatars = [1, 2, 4, 5, 6, 7, 8, 9].map(i => `/avatars/avatar${i}.png`)

const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const pwdLoading = ref(false)

const bindStudentInput = ref('')
const bindStudentLoading = ref(false)

const boundStudentId = computed(() => {
  const s = state.userInfo && state.userInfo.studentId ? String(state.userInfo.studentId).trim() : ''
  return s
})

function loadProfileFields() {
  if (state.userInfo) {
    nickname.value = state.userInfo.nickname || ''
    const c = state.userInfo.class || ''
    userClass.value = schoolClasses.includes(c) ? c : ''
    selectedAvatar.value = state.userInfo.avatarUrl || ''
  }
}

onMounted(() => {
  loadProfileFields()
  const q = route.query.tab
  if (q === 'password' || q === 'security') tab.value = 'security'
  if (q === 'email' || q === 'student') tab.value = 'student'
})

watch(() => route.query.tab, (q) => {
  if (q === 'password' || q === 'security') tab.value = 'security'
  if (q === 'profile') tab.value = 'profile'
  if (q === 'email' || q === 'student') tab.value = 'student'
})

function selectPreset(url) {
  selectedAvatar.value = url
  avatarError.value = ''
}

async function onAvatarUpload(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) {
    avatarError.value = '请选择图片文件'
    return
  }
  if (file.size > api.AVATAR_MAX_SIZE_BYTES) {
    avatarError.value = '图片不能超过 700KB'
    return
  }
  avatarError.value = ''
  try {
    const result = await api.uploadImage(file)
    selectedAvatar.value = result.url || result
  } catch (err) {
    avatarError.value = err.message || '上传失败'
  }
}

async function handleSaveProfile() {
  if (!nickname.value.trim() || !userClass.value.trim() || !schoolClasses.includes(userClass.value)) {
    showToast('请填写昵称并从列表中选择班级')
    return
  }
  saving.value = true
  try {
    const data = { nickname: nickname.value.trim(), class: userClass.value.trim() }
    if (selectedAvatar.value) data.avatarUrl = selectedAvatar.value
    await api.updateProfile(data)
    await refreshProfile()
    loadProfileFields()
    showToast('资料已保存')
    router.push('/settings')
  } catch (e) {
    showToast(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function submitBindStudent() {
  const sid = bindStudentInput.value.trim()
  if (!sid) {
    showToast('请输入学号')
    return
  }
  const okConfirm = window.confirm(
    '确定绑定该学号吗？\n\n重要提示：一个学号只能绑定一个账号；绑定成功后不可自行修改，请确保学号填写正确。'
  )
  if (!okConfirm) return
  bindStudentLoading.value = true
  try {
    await api.bindStudentId(sid)
    await refreshProfile()
    bindStudentInput.value = ''
    showToast('学号绑定成功')
  } catch (e) {
    showToast(e.message || '绑定失败')
  } finally {
    bindStudentLoading.value = false
  }
}

async function submitPassword() {
  if (!pwdForm.oldPassword || !pwdForm.newPassword || !pwdForm.confirmPassword) {
    showToast('请完整填写密码信息')
    return
  }
  if (pwdForm.newPassword.length < 6) {
    showToast('新密码至少 6 位')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) {
    showToast('两次新密码不一致')
    return
  }
  pwdLoading.value = true
  try {
    await api.changePassword(pwdForm.oldPassword, pwdForm.newPassword)
    showToast('密码已修改，请重新登录')
    logout()
    router.replace('/login')
  } catch (e) {
    showToast(e.message || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.prefs-page {
  max-width: 520px;
  margin: 0 auto;
  padding: 20px 16px 32px;
  min-height: 100%;
  background: linear-gradient(180deg, #f0f5fb 0%, var(--bg) 120px);
}

.prefs-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
}
.back-btn {
  width: 40px; height: 40px; border-radius: 12px;
  border: 1px solid var(--border); background: #fff;
  font-size: 1.5rem; line-height: 1; color: var(--text-secondary);
  cursor: pointer; transition: var(--transition);
  box-shadow: var(--shadow);
}
.back-btn:hover {
  color: var(--primary); border-color: var(--primary-light);
}
.header-text h1 {
  margin: 0; font-size: 1.5rem; font-weight: 700; color: var(--text-primary);
}
.sub { margin: 4px 0 0; font-size: 0.85rem; color: var(--text-muted); }

.tab-strip {
  display: flex; flex-wrap: wrap; gap: 8px; padding: 6px;
  background: rgba(255,255,255,0.85);
  border-radius: 14px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  margin-bottom: 20px;
}
.tab-pill {
  flex: 1; padding: 12px 16px; border: none; border-radius: 10px;
  font-size: 0.9rem; font-weight: 600; cursor: pointer;
  color: var(--text-secondary); background: transparent;
  transition: var(--transition);
}
.tab-pill:hover { color: var(--primary); }
.tab-pill.active {
  background: #fff; color: var(--primary);
  box-shadow: 0 2px 10px rgba(74, 144, 217, 0.2);
}

.card-elevated {
  background: #fff;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: 0 8px 28px rgba(30, 41, 59, 0.06);
  padding: 20px;
}
.panel-head {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 20px; padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.panel-icon {
  width: 48px; height: 48px; border-radius: 14px;
  background: linear-gradient(135deg, #E3F2FD, #E8EAF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem;
}
.panel-head h2 { margin: 0; font-size: 1.1rem; }
.panel-desc { margin: 4px 0 0; font-size: 0.8rem; color: var(--text-muted); }

.form-group { margin-bottom: 16px; }
.input-soft {
  border-radius: 10px;
  border: 1px solid var(--border);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-soft:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.12);
}
.btn-save {
  border-radius: 12px; padding: 14px; font-weight: 600;
  margin-top: 8px;
}
.hint { text-align: center; }

.avatar-section { display: flex; gap: 20px; align-items: flex-start; }
.avatar-preview {
  width: 80px; height: 80px; border-radius: 50%;
  background: var(--bg); border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: 600; color: var(--text-muted);
  overflow: hidden; flex-shrink: 0;
}
.avatar-preview.has-avatar { padding: 0; border-color: var(--primary-light); }
.avatar-preview img { width: 100%; height: 100%; object-fit: cover; }
.avatar-options { flex: 1; min-width: 0; }
.preset-grid {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;
}
.preset-btn {
  aspect-ratio: 1; border-radius: 50%; padding: 0;
  border: 2px solid var(--border); overflow: hidden;
  cursor: pointer; transition: var(--transition);
  background: var(--bg);
}
.preset-btn:hover, .preset-btn.active { border-color: var(--primary); }
.preset-btn img { width: 100%; height: 100%; object-fit: cover; }
.upload-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.text-danger { color: var(--danger); }
.form-select { cursor: pointer; appearance: auto; min-height: 44px; }
.bound-tip { font-size: 0.95rem; color: var(--text-primary); margin-bottom: 8px; }
.mb-12 { margin-bottom: 12px; }
</style>

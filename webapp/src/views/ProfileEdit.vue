<template>
  <div class="page-container">
    <div class="page-header">
      <h2>完善个人资料</h2>
      <p class="text-secondary text-sm">请填写以下必填信息后方可使用完整功能</p>
    </div>
    <div class="card">
      <!-- Avatar -->
      <div class="form-group">
        <label class="form-label">头像</label>
        <div class="avatar-section">
          <div class="avatar-preview" :class="{ 'has-avatar': selectedAvatar }">
            <img v-if="selectedAvatar" :src="selectedAvatar" alt="头像" />
            <span v-else>{{ (nickname || '?')[0] }}</span>
          </div>
          <div class="avatar-options">
            <p class="text-xs text-muted mb-8">选择预设头像或上传自定义头像（≤700KB）</p>
            <div class="preset-grid">
              <button v-for="(url, i) in presetAvatars" :key="i"
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
const selectedAvatar = ref('')
const avatarError = ref('')
const saving = ref(false)

const presetAvatars = [1, 2, 4, 5, 6, 7, 8, 9].map(i => `/avatars/avatar${i}.png`)

onMounted(() => {
  if (state.userInfo) {
    nickname.value = state.userInfo.nickname || ''
    userClass.value = state.userInfo.class || ''
    selectedAvatar.value = state.userInfo.avatarUrl || ''
  }
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
    avatarError.value = '图片大小不能超过700KB，请更换或裁剪后上传'
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

async function handleSave() {
  if (!nickname.value.trim() || !userClass.value.trim()) {
    showToast('请填写所有必填项')
    return
  }
  saving.value = true
  try {
    const data = {
      nickname: nickname.value.trim(),
      class: userClass.value.trim()
    }
    if (selectedAvatar.value) {
      data.avatarUrl = selectedAvatar.value
    }
    await api.updateProfile(data)
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
.avatar-section { display: flex; gap: 20px; align-items: flex-start; }
.avatar-preview {
  width: 80px; height: 80px; border-radius: 50%;
  background: var(--bg); border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: 600; color: var(--text-muted);
  overflow: hidden; flex-shrink: 0;
}
.avatar-preview.has-avatar { padding: 0; }
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
.upload-row { display: flex; align-items: center; gap: 12px; }
.text-danger { color: var(--danger); }
</style>

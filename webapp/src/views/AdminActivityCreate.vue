<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center mb-16">
      <h2>创建活动</h2>
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div class="card">
      <p class="hint text-sm text-muted mb-16">
        保存后，所有用户广场将出现「近期活动」入口。用户<strong>发帖时在话题中添加下方指定的 tag</strong>即视为参与。
      </p>

      <div class="form-group">
        <label class="form-label">活动名称</label>
        <input v-model.trim="form.title" class="form-input" type="text" maxlength="120" placeholder="例如：春日摄影征集" />
      </div>

      <div class="form-group">
        <label class="form-label">活动简介</label>
        <textarea
          v-model.trim="form.intro"
          class="form-textarea"
          rows="4"
          maxlength="2000"
          placeholder="活动说明、规则等"
        />
      </div>

      <div class="form-group">
        <label class="form-label">活动页背景图</label>
        <div class="bg-upload-row flex flex-wrap items-center gap-12">
          <input ref="fileRef" type="file" accept="image/*" class="sr-only" @change="onPickImage" />
          <button type="button" class="btn btn-ghost btn-sm" :disabled="uploading" @click="triggerPick">
            {{ uploading ? '上传中…' : '选择图片' }}
          </button>
          <span v-if="form.backgroundUrl" class="text-xs text-muted truncate preview-name">{{ form.backgroundUrl }}</span>
          <button v-if="form.backgroundUrl" type="button" class="btn btn-ghost btn-sm btn-clear-bg" @click="form.backgroundUrl = ''">清除</button>
        </div>
        <div v-if="form.backgroundUrl" class="bg-preview mt-8">
          <img :src="previewBg" alt="" />
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">活动 tag（不含 #，与发帖话题一致）</label>
        <input
          v-model.trim="form.tag"
          class="form-input"
          type="text"
          maxlength="24"
          placeholder="例如：摄影分享"
        />
      </div>

      <button type="button" class="btn btn-primary mt-16" :disabled="saving" @click="submit">
        {{ saving ? '保存中…' : '保存并发布' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const fileRef = ref(null)
const uploading = ref(false)
const saving = ref(false)

const form = reactive({
  title: '',
  intro: '',
  backgroundUrl: '',
  tag: '',
})

function triggerPick() {
  fileRef.value?.click()
}

const previewBg = computed(() => {
  const u = form.backgroundUrl
  if (!u) return ''
  if (/^https?:\/\//i.test(u)) return u
  if (u.startsWith('/')) return `${window.location.origin}${u}`
  return u
})

async function loadCurrent() {
  try {
    const r = await api.getActivityCampaign()
    const c = r.campaign
    if (c) {
      form.title = c.title || ''
      form.intro = c.intro || ''
      form.backgroundUrl = c.backgroundUrl || ''
      form.tag = c.tag || ''
    }
  } catch { /* ignore */ }
}

async function onPickImage(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (!f) return
  uploading.value = true
  try {
    const r = await api.uploadImage(f)
    form.backgroundUrl = r.url || ''
    showToast('图片已上传')
  } catch (err) {
    showToast(err.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function submit() {
  if (!form.title) {
    showToast('请填写活动名称')
    return
  }
  if (!form.tag) {
    showToast('请填写活动 tag')
    return
  }
  saving.value = true
  try {
    await api.saveActivityCampaign({
      title: form.title,
      intro: form.intro,
      backgroundUrl: form.backgroundUrl,
      tag: form.tag,
    })
    showToast('已保存')
    router.push('/feed')
  } catch (e) {
    showToast(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadCurrent()
})
</script>

<style scoped>
.page-container { max-width: 640px; margin: 0 auto; padding: 16px; }
.page-header h2 { font-size: 1.25rem; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 0.9rem; }
.hint strong { font-weight: 700; color: var(--text-primary); }
.bg-preview {
  max-height: 160px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}
.bg-preview img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
}
.preview-name { max-width: 220px; }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.btn-clear-bg { color: #b91c1c; }
</style>

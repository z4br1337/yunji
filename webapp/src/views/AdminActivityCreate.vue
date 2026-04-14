<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center mb-16">
      <h2>管理活动</h2>
      <button type="button" class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div class="card mb-16">
      <div class="flex justify-between items-center mb-12">
        <h3 class="section-title">活动列表</h3>
        <button type="button" class="btn btn-primary btn-sm" @click="startNew">新建活动</button>
      </div>
      <p v-if="listLoading" class="text-sm text-muted">加载中…</p>
      <p v-else-if="!campaigns.length" class="text-sm text-muted">暂无活动，点击「新建活动」创建。</p>
      <ul v-else class="campaign-list">
        <li v-for="c in campaigns" :key="c._id" class="campaign-row flex flex-wrap items-center gap-8">
          <div class="campaign-main flex-1 min-w-0">
            <span class="campaign-title">{{ c.title }}</span>
            <span class="text-xs text-muted">· tag: {{ c.tag }}</span>
            <span v-if="c.isActive" class="badge badge-on">展示中</span>
            <span v-else class="badge badge-off">未展示</span>
          </div>
          <div class="campaign-actions flex gap-8">
            <button type="button" class="btn btn-ghost btn-sm" @click="startEdit(c)">编辑</button>
            <button type="button" class="btn btn-ghost btn-sm btn-danger" @click="onDelete(c)">删除</button>
          </div>
        </li>
      </ul>
    </div>

    <div class="card">
      <h3 class="section-title mb-12">{{ editingId ? '编辑活动' : '新建活动' }}</h3>
      <p class="hint text-sm text-muted mb-16">
        勾选「在广场展示」后，用户广场将出现「近期活动」入口；仅会有一条活动处于展示中。用户<strong>发帖时在话题中添加下方指定的 tag</strong>即视为参与，并获得更高经验奖励。
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

      <label class="form-check flex items-center gap-8 mb-16">
        <input v-model="form.isActive" type="checkbox" />
        <span>在广场展示此活动（启用）</span>
      </label>

      <div class="form-actions flex flex-wrap gap-12">
        <button type="button" class="btn btn-primary" :disabled="saving" @click="submit">
          {{ saving ? '保存中…' : editingId ? '保存修改' : '保存' }}
        </button>
        <button v-if="editingId" type="button" class="btn btn-ghost" :disabled="saving" @click="startNew">取消编辑</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import * as api from '../api/index.js'

const showToast = inject('showToast')

const fileRef = ref(null)
const uploading = ref(false)
const saving = ref(false)
const listLoading = ref(false)
const campaigns = ref([])
const editingId = ref(null)

const form = reactive({
  title: '',
  intro: '',
  backgroundUrl: '',
  tag: '',
  isActive: true,
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

function resetForm() {
  form.title = ''
  form.intro = ''
  form.backgroundUrl = ''
  form.tag = ''
  form.isActive = true
}

async function loadList() {
  listLoading.value = true
  try {
    const r = await api.listActivityCampaigns()
    campaigns.value = Array.isArray(r.campaigns) ? r.campaigns : []
  } catch (e) {
    showToast(e.message || '加载列表失败')
    campaigns.value = []
  } finally {
    listLoading.value = false
  }
}

function startNew() {
  editingId.value = null
  resetForm()
}

function startEdit(c) {
  editingId.value = c._id
  form.title = c.title || ''
  form.intro = c.intro || ''
  form.backgroundUrl = c.backgroundUrl || ''
  form.tag = c.tag || ''
  form.isActive = !!c.isActive
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

async function onDelete(c) {
  if (!window.confirm(`确定删除活动「${c.title}」？此操作不可恢复。`)) return
  try {
    await api.deleteActivityCampaign(c._id)
    showToast('已删除')
    if (editingId.value === c._id) startNew()
    await loadList()
  } catch (e) {
    showToast(e.message || '删除失败')
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
    const payload = {
      title: form.title,
      intro: form.intro,
      backgroundUrl: form.backgroundUrl,
      tag: form.tag,
      isActive: form.isActive,
    }
    if (editingId.value) {
      payload.campaignId = editingId.value
    }
    await api.saveActivityCampaign(payload)
    showToast('已保存')
    await loadList()
    startNew()
  } catch (e) {
    showToast(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.page-container { max-width: 640px; margin: 0 auto; padding: 16px; }
.page-header h2 { font-size: 1.25rem; }
.section-title { font-size: 1rem; font-weight: 600; margin: 0; }
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 0.9rem; }
.hint strong { font-weight: 700; color: var(--text-primary); }
.campaign-list { list-style: none; padding: 0; margin: 0; }
.campaign-row {
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.campaign-row:last-child { border-bottom: 0; }
.campaign-title { font-weight: 600; }
.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
}
.badge-on { background: rgba(34, 197, 94, 0.15); color: #15803d; }
.badge-off { background: var(--bg-muted, #f3f4f6); color: var(--text-muted); }
.btn-danger { color: #b91c1c; }
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
.form-check { font-size: 0.9rem; cursor: pointer; user-select: none; }
.form-check input { width: 1rem; height: 1rem; }
</style>

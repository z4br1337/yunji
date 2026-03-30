<template>
  <div class="page-container">
    <div v-if="!embedded" class="page-header flex justify-between items-center">
      <h2>发布动态</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>
    <div class="card">
      <!-- Category -->
      <div class="form-group">
        <label class="form-label">分类</label>
        <div class="chip-group">
          <button v-for="cat in categories" :key="cat.key"
            class="chip" :class="{ active: category === cat.key }"
            @click="category = cat.key">
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="form-group">
        <label class="form-label">内容</label>
        <textarea class="form-textarea" v-model="content" placeholder="分享你的想法..." maxlength="2000" rows="6"></textarea>
        <span class="text-xs text-muted">{{ content.length }}/2000</span>
        <div v-if="sensitivePanelVisible" class="sensitive-panel" role="status" aria-live="polite">
          <p class="sensitive-panel-title">以下与原文一致的内容中，<strong class="sensitive-strong">红色</strong>为检测到的敏感词，请修改后再发布：</p>
          <div class="sensitive-mirror">
            <span
              v-for="(seg, i) in sensitiveSegments"
              :key="i"
              :class="{ 'sensitive-hit': seg.sensitive }"
            >{{ seg.text }}</span>
          </div>
          <p v-if="sensitiveFallbackWords.length" class="sensitive-fallback text-sm text-muted">
            词库命中：{{ sensitiveFallbackWords.join('、') }}（请在正文中调整变形或谐音写法）
          </p>
        </div>
      </div>

      <!-- Images -->
      <div class="form-group">
        <label class="form-label">图片（可选，最多9张）</label>
        <div class="image-upload-grid">
          <div v-for="(img, i) in images" :key="i" class="img-preview">
            <img :src="img.url" />
            <button class="img-remove" @click="removeImage(i)">×</button>
          </div>
          <label v-if="images.length < 9" class="img-add">
            <span>+</span>
            <input type="file" accept="image/*" multiple hidden @change="onFileSelect" />
          </label>
        </div>
      </div>

      <!-- Anonymous -->
      <div class="form-group">
        <label class="switch-row">
          <span>匿名发布</span>
          <input type="checkbox" v-model="isAnonymous" class="toggle" />
        </label>
      </div>

      <button class="btn btn-primary btn-block mt-16" :disabled="submitting" @click="handleSubmit">
        {{ submitting ? '发布中...' : '发布' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ embedded: { type: Boolean, default: false } })
import { POST_CATEGORIES } from '../utils/config.js'
import { check as sensitiveCheck, highlightSegments } from '../utils/sensitive.js'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const categories = POST_CATEGORIES
const category = ref('cognition')
const content = ref('')
const images = ref([])
const isAnonymous = ref(false)
const submitting = ref(false)

const sensitiveHighlight = computed(() => highlightSegments(content.value))

const sensitiveSegments = computed(() => {
  const segs = sensitiveHighlight.value.segments
  if (!segs || !segs.length) return []
  return segs
})

const sensitivePanelVisible = computed(() => !sensitiveHighlight.value.pass)

const sensitiveFallbackWords = computed(() => {
  if (sensitiveHighlight.value.pass) return []
  const hasRed = sensitiveSegments.value.some((s) => s.sensitive)
  if (hasRed) return []
  return sensitiveHighlight.value.words || []
})

function onFileSelect(e) {
  const files = Array.from(e.target.files)
  for (const f of files) {
    if (images.value.length >= 9) break
    images.value.push({ file: f, url: URL.createObjectURL(f) })
  }
  e.target.value = ''
}

function removeImage(i) { images.value.splice(i, 1) }

async function handleSubmit() {
  if (!content.value.trim()) { showToast('请输入内容'); return }
  const checkResult = sensitiveCheck(content.value)
  if (!checkResult.pass) {
    showToast('内容包含敏感词，无法发布，请查看下方红色标注修改')
    return
  }
  submitting.value = true

  try {
    const uploadedImages = []
    for (const img of images.value) {
      const result = await api.uploadImage(img.file)
      uploadedImages.push(result.url || result)
    }

    const data = {
      content: content.value, images: uploadedImages,
      category: category.value,
      isAnonymous: isAnonymous.value
    }

    const result = await api.createPost(data)
    showToast(`发布成功！经验+${result.expGain || 0}`)
    props.embedded ? router.replace('/publish') : router.back()
  } catch (e) {
    showToast(e.message || '发布失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.page-header h2 { font-size: 1.3rem; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  padding: 6px 14px; border-radius: 100px; font-size: 0.85rem;
  background: #F0F2F5; border: 1px solid transparent; color: var(--text-secondary);
  transition: var(--transition);
}
.chip.active { background: var(--primary); color: #fff; }
.chip:hover:not(.active) { border-color: var(--primary); }
.switch-row { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.toggle { width: 44px; height: 24px; appearance: none; background: #ccc; border-radius: 12px; position: relative; cursor: pointer; transition: var(--transition); }
.toggle:checked { background: var(--primary); }
.toggle::after { content: ''; position: absolute; width: 20px; height: 20px; background: #fff; border-radius: 50%; top: 2px; left: 2px; transition: var(--transition); }
.toggle:checked::after { left: 22px; }
.image-upload-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.img-preview { position: relative; width: 80px; height: 80px; border-radius: var(--radius-sm); overflow: hidden; }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.img-remove { position: absolute; top: 2px; right: 2px; width: 20px; height: 20px; border-radius: 50%; background: rgba(0,0,0,0.5); color: #fff; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; }
.img-add {
  width: 80px; height: 80px; border: 2px dashed var(--border); border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
  color: var(--text-muted); cursor: pointer; transition: var(--transition);
}
.img-add:hover { border-color: var(--primary); color: var(--primary); }

.sensitive-panel {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(220, 53, 69, 0.35);
  background: rgba(220, 53, 69, 0.06);
}
.sensitive-panel-title {
  margin: 0 0 10px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}
.sensitive-strong { color: #c82333; font-weight: 700; }
.sensitive-mirror {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.6;
  min-height: 2.5em;
  max-height: 220px;
  overflow-y: auto;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: var(--bg-card);
  border: 1px solid var(--border);
}
.sensitive-hit {
  color: #c82333;
  font-weight: 700;
  background: rgba(220, 53, 69, 0.18);
  border-radius: 2px;
  padding: 0 1px;
}
.sensitive-fallback { margin: 10px 0 0; }
</style>

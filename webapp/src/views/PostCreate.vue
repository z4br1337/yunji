<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
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
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { POST_CATEGORIES } from '../utils/config.js'
import { check as sensitiveCheck } from '../utils/sensitive.js'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const categories = POST_CATEGORIES
const category = ref('cognition')
const content = ref('')
const images = ref([])
const isAnonymous = ref(false)
const submitting = ref(false)

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
  submitting.value = true

  try {
    const checkResult = sensitiveCheck(content.value)
    const uploadedImages = []
    for (const img of images.value) {
      const result = await api.uploadImage(img.file)
      uploadedImages.push(result.url || result)
    }

    const data = {
      content: content.value, images: uploadedImages,
      category: category.value,
      isAnonymous: isAnonymous.value,
      flagged: !checkResult.pass,
      flaggedWords: checkResult.words,
      flaggedCategories: checkResult.categories,
      flaggedHighlighted: checkResult.highlighted
    }

    const result = await api.createPost(data)

    if (!checkResult.pass) {
      showToast('帖子包含敏感内容，已标记处理')
    } else {
      showToast(`发布成功！经验+${result.expGain || 0}`)
    }
    router.back()
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
</style>

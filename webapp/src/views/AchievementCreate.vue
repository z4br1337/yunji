<template>
  <div class="page-container">
    <div class="page-header flex justify-between items-center">
      <h2>提交闪光时刻</h2>
      <button class="btn btn-ghost btn-sm" @click="$router.back()">返回</button>
    </div>

    <div class="card">
      <!-- Section Tabs -->
      <div class="section-tabs mb-16">
        <button type="button" class="section-tab" :class="{ active: activeSection === 'virtue' }" @click="setSection('virtue')">德智体美劳</button>
        <button type="button" class="section-tab" :class="{ active: activeSection === 'growth' }" @click="setSection('growth')">三维发展</button>
      </div>

      <!-- Virtue section -->
      <div v-if="activeSection === 'virtue'" class="form-group">
        <label class="form-label">分类</label>
        <div class="chip-group">
          <button v-for="cat in achCategories" :key="cat.key" type="button" class="chip" :class="{ active: category === cat.key }" @click="category = cat.key">
            {{ cat.icon }} {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Growth section -->
      <template v-if="activeSection === 'growth'">
        <div class="form-group">
          <label class="form-label">维度</label>
          <div class="chip-group">
            <button
              v-for="dim in dimensions"
              :key="dim.key"
              type="button"
              class="chip"
              :class="{ active: dimension === dim.key }"
              @click="dimension = dim.key; subcategory = ''; growthPresetChoice = null"
            >
              {{ dim.icon }} {{ dim.label }}
            </button>
          </div>
        </div>
        <div v-if="currentDimSubs.length" class="form-group">
          <label class="form-label">子分类</label>
          <div class="chip-group">
            <button
              v-for="sub in currentDimSubs"
              :key="sub.key"
              type="button"
              class="chip"
              :class="{ active: subcategory === sub.key }"
              @click="subcategory = sub.key; growthPresetChoice = null"
            >
              {{ sub.label }}
            </button>
          </div>
        </div>
        <div v-if="dimension && subcategory && presetLines.length" class="form-group">
          <label class="form-label">具体说明</label>
          <p class="text-sm text-muted mb-8">请选择与您情况相符的一项；选「其他」时需自填标题。</p>
          <div class="growth-preset-list">
            <button
              v-for="(line, idx) in presetLines"
              :key="idx"
              type="button"
              class="growth-preset-item"
              :class="{ active: growthPresetChoice === idx }"
              @click="selectPresetTier(idx)"
            >
              <span class="growth-preset-badge">档{{ idx + 1 }}</span>
              <span class="growth-preset-text">{{ line }}</span>
            </button>
            <button
              type="button"
              class="growth-preset-item growth-preset-item--other"
              :class="{ active: growthPresetChoice === OTHER_KEY }"
              @click="selectPresetOther"
            >
              <span class="growth-preset-badge">其他</span>
              <span class="growth-preset-text">以上均不符合，自填标题</span>
            </button>
          </div>
        </div>
      </template>

      <div v-if="showTitleInput" class="form-group">
        <label class="form-label">{{ titleInputLabel }}</label>
        <input
          class="form-input"
          v-model="title"
          placeholder="例如：校运会100米短跑第三名"
          maxlength="128"
        />
      </div>
      <div class="form-group">
        <label class="form-label">描述</label>
        <textarea class="form-textarea" v-model="description" placeholder="详细描述你的闪光时刻..." rows="4" maxlength="500"></textarea>
      </div>

      <!-- Level -->
      <div class="form-group">
        <label class="form-label">蜕变等级</label>
        <p v-if="activeSection === 'growth' && typeof growthPresetChoice === 'number'" class="text-xs text-muted mb-8">已根据所选档位推荐等级，可按需调整。</p>
        <div class="chip-group">
          <button v-for="l in 5" :key="l" type="button" class="chip" :class="{ active: level === l }" @click="level = l">
            等级 {{ l }}
          </button>
        </div>
        <div class="level-guide mt-8">
          <div v-for="g in reviewGuide" :key="g.level" class="guide-row text-xs">
            <span class="guide-level">等级{{ g.level }}</span>
            <span class="guide-label">{{ g.label }}</span>
            <span class="text-muted">{{ g.desc }}</span>
          </div>
        </div>
      </div>

      <!-- Images -->
      <div class="form-group">
        <label class="form-label">请提交相关照片（奖状/证明/活动照片），至少1张</label>
        <div class="image-upload-grid">
          <div v-for="(img, i) in images" :key="i" class="img-preview">
            <img :src="img.url" alt="" />
            <button type="button" class="img-remove" @click="images.splice(i, 1)">×</button>
          </div>
          <label v-if="images.length < 9" class="img-add">
            <span>+</span>
            <input type="file" accept="image/*" multiple hidden @change="onFileSelect" />
          </label>
        </div>
      </div>

      <div class="notice-card mb-16">
        提交后需导生审核，审核通过后将获得对应经验值奖励。
      </div>

      <button type="button" class="btn btn-primary btn-block" :disabled="submitting" @click="handleSubmit">
        {{ submitting ? '提交中...' : '提交闪光时刻' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import { ACHIEVEMENT_CATEGORIES, GROWTH_DIMENSIONS, REVIEW_LEVEL_GUIDE } from '../utils/config.js'
import {
  GROWTH_OTHER_KEY,
  getGrowthPresetLines,
  growthTierToLevel,
  buildGrowthSubmitText,
} from '../utils/growthPresets.js'
import * as api from '../api/index.js'

const router = useRouter()
const showToast = inject('showToast')

const OTHER_KEY = GROWTH_OTHER_KEY

const achCategories = ACHIEVEMENT_CATEGORIES
const dimensions = GROWTH_DIMENSIONS
const reviewGuide = REVIEW_LEVEL_GUIDE

const activeSection = ref('virtue')
const category = ref('moral')
const dimension = ref('')
const subcategory = ref('')
/** @type {import('vue').Ref<number|string|null>} */
const growthPresetChoice = ref(null)
const title = ref('')
const description = ref('')
const level = ref(1)
const images = ref([])
const submitting = ref(false)

const currentDimSubs = computed(() => {
  const dim = dimensions.find((d) => d.key === dimension.value)
  return dim ? dim.subcategories : []
})

const presetLines = computed(() => getGrowthPresetLines(dimension.value, subcategory.value))

const showTitleInput = computed(
  () => activeSection.value === 'virtue' || (activeSection.value === 'growth' && growthPresetChoice.value === OTHER_KEY),
)

const titleInputLabel = computed(() => (activeSection.value === 'growth' ? '标题（其他）' : '标题'))

function setSection(s) {
  activeSection.value = s
  if (s === 'virtue') {
    growthPresetChoice.value = null
    dimension.value = ''
    subcategory.value = ''
  } else {
    title.value = ''
    growthPresetChoice.value = null
  }
}

function selectPresetTier(idx) {
  growthPresetChoice.value = idx
  level.value = growthTierToLevel(idx)
}

function selectPresetOther() {
  growthPresetChoice.value = OTHER_KEY
}

function onFileSelect(e) {
  for (const f of Array.from(e.target.files)) {
    if (images.value.length >= 9) break
    images.value.push({ file: f, url: URL.createObjectURL(f) })
  }
  e.target.value = ''
}

async function handleSubmit() {
  if (!images.value.length) {
    showToast('请提交相关照片（奖状/证明/活动照片）')
    return
  }

  let outTitle = ''
  let outDesc = description.value.trim()

  if (activeSection.value === 'virtue') {
    if (!title.value.trim()) {
      showToast('请输入标题')
      return
    }
    outTitle = title.value.trim()
  } else {
    if (!dimension.value || !subcategory.value) {
      showToast('请选择维度与子分类')
      return
    }
    if (growthPresetChoice.value === null || growthPresetChoice.value === undefined) {
      showToast('请选择具体说明')
      return
    }
    if (growthPresetChoice.value === OTHER_KEY) {
      if (!title.value.trim()) {
        showToast('请填写标题')
        return
      }
      outTitle = title.value.trim()
    } else {
      const lines = presetLines.value
      const line = lines[growthPresetChoice.value]
      if (!line) {
        showToast('选项无效，请重新选择')
        return
      }
      const built = buildGrowthSubmitText(line, outDesc)
      outTitle = built.title
      outDesc = built.description
    }
  }

  submitting.value = true
  try {
    const uploadedImages = []
    for (const img of images.value) {
      const result = await api.uploadImage(img.file)
      uploadedImages.push(result.url || result)
    }
    await api.createAchievement({
      title: outTitle,
      description: outDesc,
      category: activeSection.value === 'virtue' ? category.value : dimension.value,
      dimension: activeSection.value === 'growth' ? dimension.value : '',
      subcategory: subcategory.value,
      level: level.value,
      images: uploadedImages,
    })
    showToast('提交成功，等待导生审核')
    router.back()
  } catch (e) {
    showToast(e.message || '提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container { max-width: 600px; margin: 0 auto; padding: 16px; }
.page-header { margin-bottom: 16px; }
.section-tabs { display: flex; gap: 8px; }
.section-tab { flex: 1; padding: 10px; border-radius: var(--radius-sm); background: #F0F2F5; font-size: 0.9rem; transition: var(--transition); color: var(--text-secondary); }
.section-tab.active { background: var(--primary); color: #fff; }
.chip-group { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { padding: 6px 14px; border-radius: 100px; font-size: 0.85rem; background: #F0F2F5; border: 1px solid transparent; color: var(--text-secondary); transition: var(--transition); }
.chip.active { background: var(--primary); color: #fff; }
.level-guide { background: var(--bg); border-radius: var(--radius-sm); padding: 8px 12px; }
.guide-row { display: flex; gap: 8px; padding: 4px 0; align-items: center; }
.guide-level { font-weight: 600; color: var(--primary); min-width: 48px; }
.guide-label { font-weight: 500; min-width: 36px; }
.notice-card { background: #E8F5E9; border-radius: var(--radius-sm); padding: 12px; font-size: 0.85rem; color: #2E7D32; }
.image-upload-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.img-preview { position: relative; width: 80px; height: 80px; border-radius: var(--radius-sm); overflow: hidden; }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.img-remove { position: absolute; top: 2px; right: 2px; width: 20px; height: 20px; border-radius: 50%; background: rgba(0,0,0,0.5); color: #fff; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; }
.img-add { width: 80px; height: 80px; border: 2px dashed var(--border); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; }

.growth-preset-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.growth-preset-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  text-align: left;
  width: 100%;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-card, #fff);
  color: var(--text-primary);
  font-size: 0.82rem;
  line-height: 1.45;
  cursor: pointer;
  transition: var(--transition);
}
.growth-preset-item:hover {
  border-color: var(--primary);
  background: rgba(74, 144, 217, 0.06);
}
.growth-preset-item.active {
  border-color: var(--primary);
  background: rgba(74, 144, 217, 0.12);
  box-shadow: 0 0 0 1px var(--primary);
}
.growth-preset-item--other.active {
  border-color: #9b59b6;
  background: rgba(155, 89, 182, 0.1);
  box-shadow: 0 0 0 1px #9b59b6;
}
.growth-preset-badge {
  flex-shrink: 0;
  min-width: 40px;
  padding: 2px 8px;
  border-radius: 100px;
  background: var(--bg);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary);
}
.growth-preset-item.active .growth-preset-badge {
  background: var(--primary);
  color: #fff;
}
.growth-preset-item--other .growth-preset-badge {
  background: #ece4f5;
  color: #6c3483;
}
.growth-preset-item--other.active .growth-preset-badge {
  background: #9b59b6;
  color: #fff;
}
.growth-preset-text {
  flex: 1;
  min-width: 0;
}
</style>

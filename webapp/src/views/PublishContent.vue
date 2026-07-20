<template>
  <div class="page-container publish-content">
    <div class="publish-tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab-btn"
        :class="{ active: activeTab === t.key }"
        @click="activeTab = t.key"
      >
        <span class="tab-icon">{{ t.icon }}</span>
        <span class="tab-label">{{ t.label }}</span>
      </button>
    </div>
    <div class="publish-hero card">
      <div class="publish-hero-copy">
        <p class="publish-hero-kicker">今天想分享点什么？</p>
        <h2 class="publish-hero-title">把灵感、资料和文件，一键发出去</h2>
        <p class="publish-hero-desc">按内容类型切换，快速发布帖子或文件分享，保留你熟悉的匿名发布与话题能力。</p>
      </div>
      <div class="publish-hero-badges" aria-hidden="true">
        <span>匿名可发</span>
        <span>话题可加</span>
        <span>图片可传</span>
      </div>
    </div>
    <div class="tab-panel">
      <PostCreate v-if="activeTab === 'post'" embedded />
      <FileShare v-else-if="activeTab === 'file'" embedded />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PostCreate from './PostCreate.vue'
import FileShare from './FileShare.vue'

const tabs = [
  { key: 'post', label: '发布帖子', icon: '✏️' },
  { key: 'file', label: '文件分享', icon: '📁' },
]
const activeTab = ref('post')
</script>

<style scoped>
.publish-content { padding-top: 8px; }
.publish-tabs {
  display: flex; gap: 8px; margin-bottom: 14px;
  padding: 6px; background: rgba(255,255,255,0.72); border-radius: 18px; border: 1px solid rgba(255,255,255,0.8);
  box-shadow: 0 10px 26px rgba(255,130,0,0.06);
}
.tab-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  min-height: 54px; padding: 12px 14px; border: none; border-radius: 14px;
  background: transparent; color: var(--text-secondary); font-size: 0.92rem; font-weight: 600;
  cursor: pointer; transition: var(--transition);
}
.tab-btn:hover { color: var(--primary); background: rgba(255,130,0,0.05); }
.tab-btn.active { background: linear-gradient(135deg, #fff 0%, #fff8f1 100%); color: var(--primary); font-weight: 700; box-shadow: 0 10px 24px rgba(255,130,0,0.10); }
.tab-icon { font-size: 1.08rem; }
.tab-label { line-height: 1; }
.publish-hero {
  padding: 16px 16px 14px; margin-bottom: 14px; border-radius: 20px;
  background: linear-gradient(135deg, rgba(255,130,0,0.08), rgba(255,255,255,0.92));
  border: 1px solid rgba(255,130,0,0.08);
}
.publish-hero-copy { margin-bottom: 12px; }
.publish-hero-kicker { font-size: 0.8rem; color: var(--primary); font-weight: 700; margin-bottom: 6px; }
.publish-hero-title { font-size: 1.1rem; font-weight: 800; color: var(--text-primary); line-height: 1.35; }
.publish-hero-desc { margin-top: 6px; font-size: 0.85rem; color: var(--text-secondary); line-height: 1.55; }
.publish-hero-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.publish-hero-badges span { padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,0.75); color: var(--primary); font-size: 0.78rem; font-weight: 600; }
.tab-panel { min-height: 200px; }
@media (max-width: 480px) {
  .publish-tabs { gap: 6px; padding: 5px; }
  .tab-btn { min-height: 50px; padding: 10px 10px; font-size: 0.86rem; }
  .publish-hero { padding: 14px 14px 12px; }
  .publish-hero-title { font-size: 1rem; }
  .publish-hero-desc { font-size: 0.82rem; }
}
</style>

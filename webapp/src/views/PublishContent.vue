<template>
  <div class="page-container publish-content">
    <div class="publish-shell">
      <div class="publish-head card">
        <div class="publish-head-main">
          <div class="publish-head-copy">
            <p class="publish-head-kicker">发布</p>
            <h2 class="publish-head-title">把想法、资料和文件发给更多同学</h2>
            <p class="publish-head-desc">参考简洁的内容平台样式，保留匿名、话题和图片能力，同时更适合手机端操作。</p>
          </div>
          <div class="publish-head-meta" aria-hidden="true">
            <span>匿名发布</span>
            <span>话题互动</span>
            <span>图片上传</span>
          </div>
        </div>
        <div class="publish-tabs" role="tablist" aria-label="发布类型">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="tab-btn"
            :class="{ active: activeTab === t.key }"
            @click="activeTab = t.key"
            :aria-selected="activeTab === t.key"
            role="tab"
            type="button"
          >
            <span class="tab-icon">{{ t.icon }}</span>
            <span class="tab-label">{{ t.label }}</span>
          </button>
        </div>
      </div>

      <div class="tab-panel">
        <PostCreate v-if="activeTab === 'post'" embedded />
        <FileShare v-else-if="activeTab === 'file'" embedded />
      </div>
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
.publish-content { padding-top: 10px; }
.publish-shell { max-width: 760px; margin: 0 auto; }
.publish-head {
  padding: 18px;
  margin-bottom: 14px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(244,249,255,0.96));
  border: 1px solid rgba(27, 116, 228, 0.08);
  box-shadow: 0 10px 30px rgba(17,24,39,0.04);
}
.publish-head-main { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.publish-head-copy { flex: 1; min-width: 0; }
.publish-head-kicker {
  font-size: 0.74rem;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.publish-head-title { font-size: 1.48rem; line-height: 1.2; font-weight: 800; color: #16324f; letter-spacing: -0.02em; }
.publish-head-desc { margin-top: 8px; font-size: 0.88rem; line-height: 1.6; color: var(--text-secondary); max-width: 42em; }
.publish-head-meta {
  display: flex; flex-wrap: wrap; gap: 8px;
  align-items: flex-start; justify-content: flex-end;
  max-width: 240px;
}
.publish-head-meta span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(27, 116, 228, 0.08);
  color: #1b74e4;
  font-size: 0.78rem;
  font-weight: 700;
}
.publish-tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
  margin-top: 18px;
  border-radius: 18px;
  background: rgba(247,250,255,0.92);
  border: 1px solid rgba(27, 116, 228, 0.08);
}
.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 54px;
  padding: 12px 14px;
  border: none;
  border-radius: 14px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
}
.tab-btn:hover { color: var(--primary); background: rgba(27, 116, 228, 0.05); }
.tab-btn.active { background: linear-gradient(135deg, #fff 0%, #f3f8ff 100%); color: var(--primary); font-weight: 700; box-shadow: 0 10px 24px rgba(27, 116, 228, 0.10); }
.tab-icon { font-size: 1.08rem; }
.tab-label { line-height: 1; }
.tab-panel { min-height: 200px; }
@media (max-width: 480px) {
  .publish-content { padding-top: 6px; }
  .publish-head { padding: 14px; border-radius: 20px; }
  .publish-head-main { flex-direction: column; gap: 12px; }
  .publish-head-title { font-size: 1.12rem; }
  .publish-head-desc { font-size: 0.82rem; }
  .publish-head-meta { max-width: none; }
  .publish-tabs { gap: 6px; padding: 6px; margin-top: 14px; }
  .tab-btn { min-height: 48px; padding: 10px 10px; font-size: 0.84rem; }
}
</style>

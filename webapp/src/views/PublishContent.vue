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
    <div class="tab-panel">
      <PostCreate v-if="activeTab === 'post'" embedded />
      <FileShare v-else-if="activeTab === 'file'" embedded />
      <Achievements v-else-if="activeTab === 'achievements'" embedded />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PostCreate from './PostCreate.vue'
import FileShare from './FileShare.vue'
import Achievements from './Achievements.vue'

const tabs = [
  { key: 'post', label: '发布帖子', icon: '✏️' },
  { key: 'file', label: '文件分享', icon: '📁' },
  { key: 'achievements', label: '闪光时刻', icon: '🌟' }
]
const activeTab = ref('post')
</script>

<style scoped>
.publish-content { padding-top: 8px; }
.publish-tabs {
  display: flex; gap: 4px; margin-bottom: 16px;
  padding: 4px; background: var(--bg); border-radius: var(--radius);
}
.tab-btn {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 8px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-muted); font-size: 0.8rem;
  cursor: pointer; transition: var(--transition);
}
.tab-btn:hover { color: var(--text); background: rgba(255,255,255,0.5); }
.tab-btn.active { background: #fff; color: var(--primary); font-weight: 600; box-shadow: var(--shadow); }
.tab-icon { font-size: 1.2rem; }
.tab-panel { min-height: 200px; }
</style>

<template>
  <div class="axes-wrap">
    <p class="axes-caption text-sm text-muted mb-8">三维发展：学业 · 能力实践 · 内在成长（审核通过项按等级累计，单轴满分 100）</p>
    <h3 class="axes-title">三维坐标</h3>
    <div class="axes-svg-box">
      <svg class="axes-svg" viewBox="0 0 200 168" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <!-- 浅底 -->
        <rect x="8" y="8" width="184" height="152" rx="8" fill="#fdf2f4" opacity="0.95" />
        <!-- 底面网格示意 -->
        <path
          d="M 100 125 L 162 128 M 100 125 L 38 128 M 38 128 L 100 131 L 162 128"
          fill="none"
          stroke="#e8e0e3"
          stroke-width="0.8"
          stroke-dasharray="3 3"
        />
        <!-- Z 轴 绿 -->
        <line x1="100" y1="125" x2="100" y2="52" stroke="#27AE60" stroke-width="2.2" stroke-linecap="round" />
        <polygon points="100,48 97,56 103,56" fill="#27AE60" />
        <text x="108" y="58" class="axis-tag z-tag">Z</text>
        <!-- X 轴 红 -->
        <line x1="100" y1="125" x2="166" y2="131" stroke="#E74C3C" stroke-width="2.2" stroke-linecap="round" />
        <polygon points="170,132 162,128 164,135" fill="#E74C3C" />
        <text x="168" y="142" class="axis-tag x-tag">X</text>
        <!-- Y 轴 蓝 -->
        <line x1="100" y1="125" x2="34" y2="131" stroke="#3498DB" stroke-width="2.2" stroke-linecap="round" />
        <polygon points="30,132 38,128 36,135" fill="#3498DB" />
        <text x="22" y="142" class="axis-tag y-tag">Y</text>
        <!-- 原点 -->
        <circle cx="100" cy="125" r="3" fill="#555" />
        <!-- 数据点 -->
        <circle v-if="hasData" :cx="point.x" :cy="point.y" r="5" fill="rgba(74, 144, 217, 0.85)" stroke="#fff" stroke-width="1.5" />
        <!-- 从数据点到地面的虚线 -->
        <line
          v-if="hasData"
          :x1="point.x"
          :y1="point.y"
          :x2="floorX"
          :y2="floorY"
          stroke="#94a3b8"
          stroke-width="1"
          stroke-dasharray="4 3"
          opacity="0.7"
        />
      </svg>
    </div>
    <ul class="axes-legend text-xs text-muted">
      <li><span class="lg z">Z</span> 内在成长（inner）</li>
      <li><span class="lg x">X</span> 学业发展（academic）</li>
      <li><span class="lg y">Y</span> 能力实践（practice）</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 三轴分值 0–100，键与 GROWTH_DIMENSIONS 一致：academic, practice, inner
 * 映射到 XYZ：X=academic, Y=practice, Z=inner（与参考图 RGB 轴对应）
 */
const props = defineProps({
  scores: {
    type: Object,
    default: () => ({ academic: 0, practice: 0, inner: 0 }),
  },
})

const ox = 100
const oy = 125
const L = 58

// 单位方向（屏幕坐标，y 向下为正）
const uz = { x: 0, y: -1 }
const ux = { x: 0.867, y: 0.103 }
const uy = { x: -0.867, y: 0.103 }

const point = computed(() => {
  const rx = Math.min(1, Math.max(0, Number(props.scores.academic) / 100))
  const ry = Math.min(1, Math.max(0, Number(props.scores.practice) / 100))
  const rz = Math.min(1, Math.max(0, Number(props.scores.inner) / 100))
  const x = ox + L * (rx * ux.x + ry * uy.x + rz * uz.x)
  const y = oy + L * (rx * ux.y + ry * uy.y + rz * uz.y)
  return { x, y }
})

/** 投影到 XY 平面（近似地面） */
const floorX = computed(() => {
  const rx = Math.min(1, Math.max(0, Number(props.scores.academic) / 100))
  const ry = Math.min(1, Math.max(0, Number(props.scores.practice) / 100))
  return ox + L * (rx * ux.x + ry * uy.x)
})
const floorY = computed(() => {
  const rx = Math.min(1, Math.max(0, Number(props.scores.academic) / 100))
  const ry = Math.min(1, Math.max(0, Number(props.scores.practice) / 100))
  return oy + L * (rx * ux.y + ry * uy.y)
})

const hasData = computed(() => {
  const s = props.scores || {}
  return (Number(s.academic) || 0) + (Number(s.practice) || 0) + (Number(s.inner) || 0) > 0
})
</script>

<style scoped>
.axes-wrap {
  padding: 12px 10px 14px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.axes-caption { margin: 0; line-height: 1.45; }
.axes-title {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
}
.axes-svg-box {
  max-width: 100%;
  margin: 0 auto;
}
.axes-svg {
  width: 100%;
  max-height: 220px;
  height: auto;
  display: block;
}
.axis-tag {
  font-size: 11px;
  font-weight: 800;
  fill: var(--text-secondary);
}
.z-tag { fill: #1e8449; }
.x-tag { fill: #c0392b; }
.y-tag { fill: #2874a6; }
.axes-legend {
  margin: 10px 0 0;
  padding: 0 8px;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  justify-content: center;
  line-height: 1.4;
}
.axes-legend li { display: flex; align-items: center; gap: 6px; }
.lg {
  display: inline-flex;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  color: #fff;
}
.lg.z { background: #27AE60; }
.lg.x { background: #E74C3C; }
.lg.y { background: #3498DB; }
</style>

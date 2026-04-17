<template>
  <div class="radar-wrap card">
    <p class="radar-caption text-sm text-muted mb-8">可视化呈现：通过雷达图方式让成长轨迹一目了然</p>
    <h3 class="radar-title">德智体美劳发展</h3>
    <div class="radar-svg-box">
      <svg class="radar-svg" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <!-- 同心五边形网格 -->
        <g v-for="(frac, gi) in gridFracs" :key="'g' + gi" class="grid-ring">
          <polygon
            :points="ringPoints(frac)"
            fill="none"
            stroke="var(--border)"
            stroke-width="1"
          />
        </g>
        <!-- 轴线 -->
        <g v-for="(ax, i) in axes" :key="'a' + i">
          <line
            :x1="cx"
            :y1="cy"
            :x2="ax.lx"
            :y2="ax.ly"
            stroke="var(--border)"
            stroke-width="1"
          />
        </g>
        <!-- 数据多边形 -->
        <polygon
          v-if="dataPoints"
          :points="dataPoints"
          fill="rgba(74, 144, 217, 0.22)"
          stroke="var(--primary)"
          stroke-width="2"
          stroke-linejoin="round"
        />
        <!-- 顶点标签 -->
        <g v-for="(ax, i) in axes" :key="'t' + i">
          <text
            :x="ax.tx"
            :y="ax.ty"
            text-anchor="middle"
            dominant-baseline="middle"
            class="axis-label"
          >{{ ax.label }}</text>
        </g>
      </svg>
    </div>
    <p class="radar-foot text-xs text-muted text-center mt-8">满分 100 分 / 维；等级分 2、4、6、8、10 分 · 全方位发展</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ACHIEVEMENT_CATEGORIES } from '../utils/config.js'

const props = defineProps({
  /** 各 key 分值 0–100，与 ACHIEVEMENT_CATEGORIES 顺序一致 */
  scores: { type: Object, required: true },
})

const cx = 110
const cy = 110
const rMax = 78
const labelR = 96

/** 从正上方顺时针：德 → 智 → 体 → 美 → 劳 */
const axes = computed(() => {
  const n = ACHIEVEMENT_CATEGORIES.length
  return ACHIEVEMENT_CATEGORIES.map((cat, i) => {
    const theta = -Math.PI / 2 + (i * 2 * Math.PI) / n
    const lx = cx + rMax * Math.cos(theta)
    const ly = cy + rMax * Math.sin(theta)
    const tx = cx + labelR * Math.cos(theta)
    const ty = cy + labelR * Math.sin(theta)
    return { key: cat.key, label: cat.label, lx, ly, tx, ty }
  })
})

const gridFracs = [0.25, 0.5, 0.75, 1]

function ringPoints(frac) {
  const n = ACHIEVEMENT_CATEGORIES.length
  const pts = []
  for (let i = 0; i < n; i++) {
    const theta = -Math.PI / 2 + (i * 2 * Math.PI) / n
    const r = rMax * frac
    pts.push(`${cx + r * Math.cos(theta)},${cy + r * Math.sin(theta)}`)
  }
  return pts.join(' ')
}

const dataPoints = computed(() => {
  const n = ACHIEVEMENT_CATEGORIES.length
  const parts = []
  for (let i = 0; i < n; i++) {
    const key = ACHIEVEMENT_CATEGORIES[i].key
    const v = Math.min(100, Math.max(0, Number(props.scores[key]) || 0))
    const frac = v / 100
    const theta = -Math.PI / 2 + (i * 2 * Math.PI) / n
    const r = rMax * frac
    parts.push(`${cx + r * Math.cos(theta)},${cy + r * Math.sin(theta)}`)
  }
  return parts.join(' ')
})
</script>

<style scoped>
.radar-wrap {
  padding: 16px 14px 18px;
  margin-bottom: 16px;
  border: 1px solid var(--border);
}
.radar-caption { margin: 0; line-height: 1.45; }
.radar-title {
  margin: 0 0 12px;
  font-size: 1.05rem;
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
}
.radar-svg-box {
  max-width: 320px;
  margin: 0 auto;
}
.radar-svg {
  width: 100%;
  height: auto;
  display: block;
}
.axis-label {
  font-size: 13px;
  font-weight: 700;
  fill: var(--text-primary);
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.radar-foot { margin: 0; line-height: 1.4; }
</style>

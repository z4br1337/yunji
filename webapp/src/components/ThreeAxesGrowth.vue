<template>
  <div class="axes-wrap">
    <p class="axes-caption text-sm text-muted mb-8">
      三维发展：学业 · 能力实践 · 内在成长（审核通过项按等级累计，单轴满分 100）
    </p>
    <h3 class="axes-title">三维坐标</h3>

    <div class="axes-svg-box">
      <svg class="axes-svg" viewBox="0 0 320 280" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <linearGradient id="axes-floor-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#fce8ee" />
            <stop offset="55%" stop-color="#fdf2f6" />
            <stop offset="100%" stop-color="#e8eef5" />
          </linearGradient>
          <linearGradient id="axes-wall-grad" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#e2e8f0" stop-opacity="0.35" />
            <stop offset="100%" stop-color="#f1f5f9" stop-opacity="0.15" />
          </linearGradient>
          <filter id="axes-data-glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="1.2" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="axes-marker-shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="1" stdDeviation="2" flood-opacity="0.35" />
          </filter>
        </defs>

        <!-- 立体线框：底面 + 后侧竖棱（营造景深） -->
        <polygon :points="floorFace" fill="url(#axes-floor-grad)" stroke="#d4c4cc" stroke-width="1.1" opacity="0.98" />
        <polygon :points="leftWallFace" fill="url(#axes-wall-grad)" stroke="#cbd5e1" stroke-width="0.9" opacity="0.85" />
        <path :d="backEdges" fill="none" stroke="#94a3b8" stroke-width="1" stroke-linecap="round" opacity="0.65" />

        <!-- 底面网格 -->
        <g v-for="(seg, gi) in floorGrid" :key="'fg' + gi">
          <line
            :x1="seg.x1"
            :y1="seg.y1"
            :x2="seg.x2"
            :y2="seg.y2"
            stroke="#dcd6dc"
            stroke-width="0.65"
            stroke-dasharray="3 4"
            opacity="0.75"
          />
        </g>

        <!-- 坐标轴骨架（浅色全轴） -->
        <line :x1="O.x" :y1="O.y" :x2="axisFull.X.x" :y2="axisFull.X.y" stroke="#f5c6c6" stroke-width="2" stroke-linecap="round" />
        <line :x1="O.x" :y1="O.y" :x2="axisFull.Y.x" :y2="axisFull.Y.y" stroke="#c5ddf5" stroke-width="2" stroke-linecap="round" />
        <line :x1="O.x" :y1="O.y" :x2="axisFull.Z.x" :y2="axisFull.Z.y" stroke="#b8e6c8" stroke-width="2" stroke-linecap="round" />

        <!-- 分维度数据：沿各轴单独绘制得分段（与雷达「每维一条边」同理） -->
        <g filter="url(#axes-data-glow)">
          <line
            :x1="O.x"
            :y1="O.y"
            :x2="segX.x"
            :y2="segX.y"
            stroke="#E74C3C"
            stroke-width="5.5"
            stroke-linecap="round"
            class="data-seg data-seg--x"
          />
          <line
            :x1="O.x"
            :y1="O.y"
            :x2="segY.x"
            :y2="segY.y"
            stroke="#3498DB"
            stroke-width="5.5"
            stroke-linecap="round"
            class="data-seg data-seg--y"
          />
          <line
            :x1="O.x"
            :y1="O.y"
            :x2="segZ.x"
            :y2="segZ.y"
            stroke="#27AE60"
            stroke-width="5.5"
            stroke-linecap="round"
            class="data-seg data-seg--z"
          />
        </g>

        <!-- 轴端箭头（仅锥尖，避免遮挡彩色得分段） -->
        <g class="axis-arrows">
          <polygon :points="arrowHeadX" fill="#C0392B" />
          <polygon :points="arrowHeadY" fill="#2874A6" />
          <polygon :points="arrowHeadZ" fill="#1E8449" />
        </g>

        <!-- 分轴端点标记（高分时略放大） -->
        <g filter="url(#axes-marker-shadow)">
          <circle :cx="segX.x" :cy="segX.y" :r="markerR(academic)" fill="#fff" stroke="#E74C3C" :stroke-width="markerStroke(academic)" />
          <circle :cx="segY.x" :cy="segY.y" :r="markerR(practice)" fill="#fff" stroke="#3498DB" :stroke-width="markerStroke(practice)" />
          <circle :cx="segZ.x" :cy="segZ.y" :r="markerR(inner)" fill="#fff" stroke="#27AE60" :stroke-width="markerStroke(inner)" />
        </g>

        <!-- 合成点：向量合成位置（细虚线连到地面） -->
        <circle
          v-if="hasData"
          :cx="combined.x"
          :cy="combined.y"
          r="7"
          fill="rgba(142, 68, 173, 0.92)"
          stroke="#fff"
          stroke-width="2.5"
          class="combined-dot"
        />
        <line
          v-if="hasData"
          :x1="combined.x"
          :y1="combined.y"
          :x2="floorProj.x"
          :y2="floorProj.y"
          stroke="#64748b"
          stroke-width="1.2"
          stroke-dasharray="5 4"
          opacity="0.85"
        />

        <!-- 各数据点得分标注（偏移避免重叠） -->
        <g class="point-score-labels" pointer-events="none">
          <text :x="labelPosX.x" :y="labelPosX.y" class="point-label point-label--x">{{ labelXText }}</text>
          <text :x="labelPosY.x" :y="labelPosY.y" class="point-label point-label--y">{{ labelYText }}</text>
          <text :x="labelPosZ.x" :y="labelPosZ.y" class="point-label point-label--z">{{ labelZText }}</text>
          <text v-if="hasData" :x="labelPosComb.x" :y="labelPosComb.y" class="point-label point-label--comb">{{ labelCombText }}</text>
        </g>

        <text :x="axisFull.X.x + 6" :y="axisFull.X.y + 4" class="axis-tag x-tag">X</text>
        <text :x="axisFull.Y.x - 14" :y="axisFull.Y.y + 6" class="axis-tag y-tag">Y</text>
        <text :x="axisFull.Z.x + 8" :y="axisFull.Z.y - 2" class="axis-tag z-tag">Z</text>
        <circle :cx="O.x" :cy="O.y" r="3.5" fill="#334155" />
      </svg>
    </div>

    <!-- 与雷达图类似：每维独立分值条 + 数字，便于对比各维变化 -->
    <div class="dim-meters" role="group" aria-label="三维发展各维度得分">
      <div
        v-for="row in dimensionRows"
        :key="row.key"
        class="dim-meter"
      >
        <span class="dim-meter-icon" aria-hidden="true">{{ row.icon }}</span>
        <span class="dim-meter-label">{{ row.label }}</span>
        <div class="dim-meter-track" :title="`${row.label} ${row.score} 分`">
          <div
            class="dim-meter-fill"
            :class="'dim-meter-fill--' + row.key"
            :style="{ width: clampedPct(row.score) + '%' }"
          />
        </div>
        <span class="dim-meter-val" :class="{ 'dim-meter-val--hot': row.score >= 60 }">{{ row.score }}</span>
      </div>
    </div>

    <ul class="axes-legend text-xs text-muted">
      <li><span class="lg z">内在</span> 内在成长（Z）· 紫色为合成位置</li>
      <li><span class="lg x">学业</span> 学业发展（X）</li>
      <li><span class="lg y">实践</span> 能力实践（Y）· 图上「总分」为三轴得分之和（最高 300）</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { GROWTH_DIMENSIONS } from '../utils/config.js'

/**
 * 三轴分值 0–100：academic→X，practice→Y，inner→Z
 * 展示：各轴中文简称标注、三轴累计总分、分维进度条与合成点
 */
const props = defineProps({
  scores: {
    type: Object,
    default: () => ({ academic: 0, practice: 0, inner: 0 }),
  },
})

/** 扩大轴长与画布，使低分时段点间距在视觉上更明显、不易重叠 */
const O = { x: 160, y: 188 }

/** 轴方向（与斜二测/原稿一致，单位向量） */
const ux = { x: 0.867, y: 0.103 }
const uy = { x: -0.867, y: 0.103 }
const uz = { x: 0, y: -1 }
function norm(v) {
  const len = Math.hypot(v.x, v.y) || 1
  return { x: v.x / len, y: v.y / len }
}
const uxn = norm(ux)
const uyn = norm(uy)
const uzn = norm(uz)

/** 单轴最大像素长度（原 58 → 100，同比放大坐标系） */
const L = 100

const axisFull = computed(() => ({
  X: { x: O.x + L * uxn.x, y: O.y + L * uxn.y },
  Y: { x: O.x + L * uyn.x, y: O.y + L * uyn.y },
  Z: { x: O.x + L * uzn.x, y: O.y + L * uzn.y },
}))

function tipAlong(dir, frac) {
  const t = Math.min(1, Math.max(0, frac))
  return { x: O.x + L * t * dir.x, y: O.y + L * t * dir.y }
}

/** 标注锚点：0 分时沿轴略外移，避免与原点、合成点完全重叠 */
function tipForLabel(dir, score) {
  const t =
    score <= 0 ? 0.08 : Math.min(1, Math.max(0, score) / 100)
  return { x: O.x + L * t * dir.x, y: O.y + L * t * dir.y }
}

function perpOffset(dir, dist, sign) {
  return { x: -dir.y * dist * sign, y: dir.x * dist * sign }
}

const academic = computed(() => Math.min(100, Math.max(0, Number(props.scores?.academic) || 0)))
const practice = computed(() => Math.min(100, Math.max(0, Number(props.scores?.practice) || 0)))
const inner = computed(() => Math.min(100, Math.max(0, Number(props.scores?.inner) || 0)))

const segX = computed(() => tipAlong(uxn, academic.value / 100))
const segY = computed(() => tipAlong(uyn, practice.value / 100))
const segZ = computed(() => tipAlong(uzn, inner.value / 100))

const combined = computed(() => {
  const rx = academic.value / 100
  const ry = practice.value / 100
  const rz = inner.value / 100
  return {
    x: O.x + L * (rx * uxn.x + ry * uyn.x + rz * uzn.x),
    y: O.y + L * (rx * uxn.y + ry * uyn.y + rz * uzn.y),
  }
})

const floorProj = computed(() => ({
  x: O.x + L * ((academic.value / 100) * uxn.x + (practice.value / 100) * uyn.x),
  y: O.y + L * ((academic.value / 100) * uxn.y + (practice.value / 100) * uyn.y),
}))

const hasData = computed(() => academic.value + practice.value + inner.value > 0)

/** 与 GROWTH_DIMENSIONS 对应的中文简称（图上标注用） */
const labelXText = computed(() => `学业 ${academic.value}`)
const labelYText = computed(() => `实践 ${practice.value}`)
const labelZText = computed(() => `内在 ${inner.value}`)
/** 三轴单项满分各 100，总分最高 300 */
const labelCombText = computed(() => {
  const sum = academic.value + practice.value + inner.value
  return `总分 ${sum}`
})

const labelPosX = computed(() => {
  const base = tipForLabel(uxn, academic.value)
  const p = perpOffset(uxn, 26, 1)
  return { x: base.x + p.x, y: base.y + p.y }
})
const labelPosY = computed(() => {
  const base = tipForLabel(uyn, practice.value)
  const p = perpOffset(uyn, 26, -1)
  return { x: base.x + p.x, y: base.y + p.y }
})
const labelPosZ = computed(() => {
  const base = tipForLabel(uzn, inner.value)
  return { x: base.x + 22, y: base.y + 6 }
})
const labelPosComb = computed(() => ({
  x: combined.value.x + 10,
  y: combined.value.y - 20,
}))

/** 底面：沿 X、Y 张成的平行四边形 */
const floorFace = computed(() => {
  const p0 = `${O.x},${O.y}`
  const p1 = `${axisFull.value.X.x},${axisFull.value.X.y}`
  const p2 = `${O.x + L * uxn.x + L * uyn.x},${O.y + L * uxn.y + L * uyn.y}`
  const p3 = `${axisFull.value.Y.x},${axisFull.value.Y.y}`
  return `${p0} ${p1} ${p2} ${p3}`
})

/** 左后竖面（沿 Y + Z），增强立体感 */
const leftWallFace = computed(() => {
  const bx = O.x + L * uyn.x
  const by = O.y + L * uyn.y
  const p0 = `${O.x},${O.y}`
  const p1 = `${bx},${by}`
  const p2 = `${bx},${by + L * uzn.y}`
  const p3 = `${O.x},${O.y + L * uzn.y}`
  return `${p0} ${p1} ${p2} ${p3}`
})

const backEdges = computed(() => {
  const bx = O.x + L * uxn.x + L * uyn.x
  const by = O.y + L * uxn.y + L * uyn.y
  const top = `${bx},${by + L * uzn.y}`
  return `M ${bx} ${by} L ${top}`
})

/** 底面浅网格 */
const floorGrid = computed(() => {
  const segs = []
  const n = 4
  for (let i = 1; i < n; i++) {
    const t = i / n
    const sx = O.x + t * L * uxn.x
    const sy = O.y + t * L * uxn.y
    const ex = sx + L * uyn.x
    const ey = sy + L * uyn.y
    segs.push({ x1: sx, y1: sy, x2: ex, y2: ey })
  }
  for (let j = 1; j < n; j++) {
    const t = j / n
    const sx = O.x + t * L * uyn.x
    const sy = O.y + t * L * uyn.y
    const ex = sx + L * uxn.x
    const ey = sy + L * uxn.y
    segs.push({ x1: sx, y1: sy, x2: ex, y2: ey })
  }
  return segs
})

function arrowHead(tip, dir) {
  const back = 10
  const spread = 4.5
  const dx = -dir.x * back
  const dy = -dir.y * back
  const px = -dir.y * spread
  const py = dir.x * spread
  const tx = tip.x
  const ty = tip.y
  return `${tx},${ty} ${tx + dx + px},${ty + dy + py} ${tx + dx - px},${ty + dy - py}`
}

const arrowHeadX = computed(() => arrowHead(axisFull.value.X, uxn))
const arrowHeadY = computed(() => arrowHead(axisFull.value.Y, uyn))
const arrowHeadZ = computed(() => arrowHead(axisFull.value.Z, uzn))

function markerR(score) {
  const s = Math.min(100, Math.max(0, score))
  return s >= 80 ? 7.5 : s >= 40 ? 6.5 : 5.5
}

function markerStroke(score) {
  const s = Math.min(100, Math.max(0, score))
  return s >= 80 ? 3 : 2.2
}

const dimensionRows = computed(() =>
  GROWTH_DIMENSIONS.map((d) => ({
    key: d.key,
    label: d.label,
    icon: d.icon,
    score:
      d.key === 'academic'
        ? academic.value
        : d.key === 'practice'
          ? practice.value
          : inner.value,
  })),
)

function clampedPct(n) {
  return Math.min(100, Math.max(0, Number(n) || 0))
}
</script>

<style scoped>
.axes-wrap {
  padding: 12px 10px 14px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.axes-caption {
  margin: 0;
  line-height: 1.45;
}
.axes-title {
  margin: 0 0 10px;
  font-size: 1rem;
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
}

.dim-meters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
  margin-bottom: 6px;
  padding: 12px 10px;
  border-radius: var(--radius-sm, 8px);
  background: linear-gradient(180deg, var(--bg-card, #fff) 0%, rgba(248, 250, 252, 0.9) 100%);
  border: 1px solid var(--border);
}
.dim-meter {
  display: grid;
  grid-template-columns: 22px 4.5rem 1fr 2.25rem;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
}
.dim-meter-icon {
  text-align: center;
  font-size: 1rem;
}
.dim-meter-label {
  color: var(--text-secondary);
  white-space: nowrap;
}
.dim-meter-track {
  height: 12px;
  border-radius: 6px;
  background: #e8ecf1;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
}
.dim-meter-fill {
  height: 100%;
  border-radius: 6px;
  min-width: 0;
  transition: width 0.45s cubic-bezier(0.33, 1, 0.68, 1);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.35) inset;
}
.dim-meter-fill--academic {
  background: linear-gradient(90deg, #f1948a, #e74c3c);
}
.dim-meter-fill--practice {
  background: linear-gradient(90deg, #5dade2, #3498db);
}
.dim-meter-fill--inner {
  background: linear-gradient(90deg, #58d68d, #27ae60);
}
.dim-meter-val {
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  text-align: right;
  color: var(--text-primary);
  font-size: 0.9rem;
}
.dim-meter-val--hot {
  color: var(--primary, #4a90d9);
}

.axes-svg-box {
  max-width: 100%;
  margin: 0 auto;
  min-height: 240px;
}
.axes-svg {
  width: 100%;
  min-height: 260px;
  max-height: 380px;
  height: auto;
  display: block;
}
.point-label {
  font-size: 13px;
  font-weight: 800;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  paint-order: stroke fill;
  stroke: rgba(255, 255, 255, 0.95);
  stroke-width: 3px;
  stroke-linejoin: round;
}
.point-label--x {
  fill: #a93226;
}
.point-label--y {
  fill: #1f618d;
}
.point-label--z {
  fill: #1e8449;
}
.point-label--comb {
  fill: #6c3483;
  font-size: 12px;
  font-weight: 800;
}
.axis-tag {
  font-size: 11px;
  font-weight: 800;
}
.z-tag {
  fill: #1e8449;
}
.x-tag {
  fill: #922b21;
}
.y-tag {
  fill: #1b4f72;
}
.combined-dot {
  filter: drop-shadow(0 2px 4px rgba(142, 68, 173, 0.45));
}

.axes-legend {
  margin: 10px 0 0;
  padding: 0 8px;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  justify-content: center;
  line-height: 1.45;
}
.axes-legend li {
  display: flex;
  align-items: center;
  gap: 6px;
}
.lg {
  display: inline-flex;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 4px;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 800;
  color: #fff;
}
.lg.z {
  background: #27ae60;
}
.lg.x {
  background: #e74c3c;
}
.lg.y {
  background: #3498db;
}

@media (max-width: 400px) {
  .dim-meter {
    grid-template-columns: 20px 4rem 1fr 2rem;
    font-size: 0.75rem;
  }
}
</style>

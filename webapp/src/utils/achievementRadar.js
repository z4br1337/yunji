import { ACHIEVEMENT_CATEGORIES, GROWTH_DIMENSIONS } from './config.js'

/** 闪光时刻等级对应得分（雷达图 / 三维轴累计，单维满分 100） */
export const ACHIEVEMENT_LEVEL_POINTS = {
  1: 2,
  2: 4,
  3: 6,
  4: 8,
  5: 10,
}

const VIRTUE_KEYS = ACHIEVEMENT_CATEGORIES.map((c) => c.key)
const GROWTH_KEYS = GROWTH_DIMENSIONS.map((d) => d.key)

/**
 * 从一条成果记录解析「三维发展」维度键（学业 / 实践 / 内在）。
 * 后续若增加新维度，只需扩展 GROWTH_DIMENSIONS 与可视化组件映射。
 * @param {{ category?: string, dimension?: string }} a
 * @returns {string|null}
 */
export function resolveGrowthDimensionKey(a) {
  if (!a) return null
  const c = (a.category || '').trim()
  if (GROWTH_KEYS.includes(c)) return c
  const d = (a.dimension || '').trim()
  if (GROWTH_KEYS.includes(d)) return d
  return null
}

/**
 * 根据「我的」已加载成果列表，按审核通过项累计五育得分（每维封顶 100）。
 * @param {Array<{ category: string, level: number, status: string }>} achievements
 */
export function scoresFromApprovedAchievements(achievements) {
  const sums = Object.fromEntries(VIRTUE_KEYS.map((k) => [k, 0]))
  for (const a of achievements || []) {
    if (a.status !== 'approved') continue
    const cat = a.category
    if (sums[cat] === undefined) continue
    const lv = Math.min(5, Math.max(1, Number(a.level) || 1))
    const add = ACHIEVEMENT_LEVEL_POINTS[lv] || 0
    sums[cat] = Math.min(100, sums[cat] + add)
  }
  return sums
}

/**
 * 三维发展闪光时刻（学业 / 能力实践 / 内在成长）审核通过项累计分，单轴封顶 100。
 * @param {Array<{ category?: string, dimension?: string, level: number, status: string }>} achievements
 */
export function scoresFromApprovedGrowthAchievements(achievements) {
  const sums = Object.fromEntries(GROWTH_KEYS.map((k) => [k, 0]))
  for (const a of achievements || []) {
    if (a.status !== 'approved') continue
    const key = resolveGrowthDimensionKey(a)
    if (!key || sums[key] === undefined) continue
    const lv = Math.min(5, Math.max(1, Number(a.level) || 1))
    const add = ACHIEVEMENT_LEVEL_POINTS[lv] || 0
    sums[key] = Math.min(100, sums[key] + add)
  }
  return sums
}

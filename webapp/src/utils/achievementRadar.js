import { ACHIEVEMENT_CATEGORIES } from './config.js'

/** 闪光时刻等级对应得分（雷达图累计，单维满分 100） */
export const ACHIEVEMENT_LEVEL_POINTS = {
  1: 2,
  2: 4,
  3: 6,
  4: 8,
  5: 10,
}

const KEYS = ACHIEVEMENT_CATEGORIES.map((c) => c.key)

/**
 * 根据「我的」已加载成果列表，按审核通过项累计五育得分（每维封顶 100）。
 * @param {Array<{ category: string, level: number, status: string }>} achievements
 */
export function scoresFromApprovedAchievements(achievements) {
  const sums = Object.fromEntries(KEYS.map((k) => [k, 0]))
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

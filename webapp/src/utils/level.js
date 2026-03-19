import {
  LEVEL_TABLE, EXP_RULES, ACHIEVEMENT_CATEGORIES,
  ACHIEVEMENT_TITLES, POST_COUNT_TITLES
} from './config.js'

export function getLevelInfo(exp) {
  exp = exp || 0
  let current = LEVEL_TABLE[0]
  for (let i = LEVEL_TABLE.length - 1; i >= 0; i--) {
    if (exp >= LEVEL_TABLE[i].exp) { current = LEVEL_TABLE[i]; break }
  }
  const next = LEVEL_TABLE.find(r => r.level === current.level + 1) || null
  const expInLevel = exp - current.exp
  const expToNext = next ? next.exp - current.exp : 0
  return {
    level: current.level, title: current.title, coefficient: current.coefficient,
    currentExp: exp, expInLevel, expToNext,
    progress: next ? Math.min(expInLevel / expToNext, 1) : 1,
    isMax: !next,
    nextLevelExp: next ? next.exp : null,
    nextTitle: next ? next.title : null
  }
}

export function calcPostExp() { return EXP_RULES.POST_PUBLISH }

export function calcAchievementExp(level) {
  return Math.min(EXP_RULES.ACHIEVEMENT_BASE * level, EXP_RULES.ACHIEVEMENT_MAX)
}

export function getAchievementTitles(counts) {
  counts = counts || {}
  const titles = []
  for (const cat of ACHIEVEMENT_CATEGORIES) {
    const count = counts[cat.key] || 0
    if (count > 0) {
      const idx = Math.min(count, 5) - 1
      const list = ACHIEVEMENT_TITLES[cat.key]
      if (list && list[idx]) {
        titles.push({
          category: cat.key, categoryLabel: cat.label,
          categoryColor: cat.color, categoryIcon: cat.icon,
          level: idx + 1, title: list[idx], count
        })
      }
    }
  }
  return titles
}

export function getHighestAchievementTitle(counts) {
  const titles = getAchievementTitles(counts)
  if (!titles.length) return null
  return titles.reduce((a, b) => b.level > a.level ? b : a)
}

export function getPostCountTitle(postCount) {
  postCount = postCount || 0
  let current = null
  for (let i = POST_COUNT_TITLES.length - 1; i >= 0; i--) {
    if (postCount >= POST_COUNT_TITLES[i].count) { current = POST_COUNT_TITLES[i]; break }
  }
  const idx = current ? POST_COUNT_TITLES.indexOf(current) : -1
  const next = idx < POST_COUNT_TITLES.length - 1 ? POST_COUNT_TITLES[idx + 1] : null
  return {
    current, next, postCount,
    progress: next ? postCount / next.count : (current ? 1 : 0)
  }
}

export function getUserBadges(user) {
  const badges = []
  if (user.role === 'admin') badges.push({ type: 'role', label: '导生', color: '#E74C3C', priority: 1 })
  const lvl = getLevelInfo(user.exp)
  badges.push({ type: 'level', label: `Lv${lvl.level} ${lvl.title}`, color: '#4A90D9', priority: 2 })
  const highest = getHighestAchievementTitle(user.achievementCounts)
  if (highest) badges.push({ type: 'achievement', label: highest.title, color: highest.categoryColor, priority: 3 })
  const pt = getPostCountTitle(user.postCount)
  if (pt.current) badges.push({ type: 'postCount', label: pt.current.title, color: '#27AE60', priority: 4 })
  badges.sort((a, b) => a.priority - b.priority)
  return badges
}

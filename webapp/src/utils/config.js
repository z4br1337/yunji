/**
 * 云迹 Web 版 - 运行时配置
 */

export const LOCAL_TEST_MODE = true

export const API_BASE_URL = '/api'

export const PAGE_SIZE = 20

export const ACHIEVEMENT_CATEGORIES = [
  { key: 'moral', label: '德', icon: '🏅', color: '#E74C3C' },
  { key: 'intellectual', label: '智', icon: '📚', color: '#3498DB' },
  { key: 'physical', label: '体', icon: '⚽', color: '#2ECC71' },
  { key: 'aesthetic', label: '美', icon: '🎨', color: '#9B59B6' },
  { key: 'labor', label: '劳', icon: '🔧', color: '#F39C12' }
]

export const ACHIEVEMENT_MAX_LEVEL = 5

export const ACHIEVEMENT_TITLES = {
  moral:        ['品德萌芽', '友善新星', '奉献能手', '道德标兵', '时代楷模'],
  intellectual: ['学习萌芽', '智慧新星', '学术能手', '创新标兵', '卓越学者'],
  physical:     ['运动萌芽', '活力新星', '运动能手', '体育标兵', '冠军楷模'],
  aesthetic:    ['艺术萌芽', '才艺新星', '文艺能手', '美育标兵', '艺术大师'],
  labor:        ['劳动萌芽', '勤劳新星', '实践能手', '劳动标兵', '工匠楷模']
}

export const POST_COUNT_TITLES = [
  { count: 50,   title: '记录初心者' },
  { count: 100,  title: '坚持探索者' },
  { count: 500,  title: '成长守望者' },
  { count: 1000, title: '青春记家' }
]

export const LEVEL_TABLE = [
  { level: 1,  exp: 0,      coefficient: 1, title: '萤卵待萌' },
  { level: 2,  exp: 50,     coefficient: 1, title: '幼虫潜行' },
  { level: 3,  exp: 150,    coefficient: 1, title: '初识微光' },
  { level: 4,  exp: 250,    coefficient: 2, title: '暗夜寻路' },
  { level: 5,  exp: 400,    coefficient: 2, title: '萤火初燃' },
  { level: 6,  exp: 650,    coefficient: 2, title: '流萤试飞' },
  { level: 7,  exp: 1000,   coefficient: 3, title: '七点星芒' },
  { level: 8,  exp: 1600,   coefficient: 3, title: '月下独舞' },
  { level: 9,  exp: 2500,   coefficient: 3, title: '萤群共鸣' },
  { level: 10, exp: 5000,   coefficient: 4, title: '破蛹成萤' },
  { level: 11, exp: 10000,  coefficient: 4, title: '双翼振频' },
  { level: 12, exp: 20000,  coefficient: 4, title: '夜巡者' },
  { level: 13, exp: 50000,  coefficient: 5, title: '萤火灯塔' },
  { level: 14, exp: 100000, coefficient: 5, title: '盛夏极光' },
  { level: 15, exp: 500000, coefficient: 5, title: '萤火传承' }
]

export const EXP_RULES = {
  CREATE_ACCOUNT: 10,
  POST_PUBLISH: 10,
  ACHIEVEMENT_BASE: 500,
  ACHIEVEMENT_LEVEL_MULTIPLIER: 500,
  ACHIEVEMENT_MAX: 2500,
  ACHIEVEMENT_UNLOCK: 50
}

export const POST_CATEGORIES = [
  { key: 'cognition', label: '认知升级站' },
  { key: 'knowledge', label: '知识补给站' },
  { key: 'energy', label: '能量加油站' },
  { key: 'fun', label: '娱乐研究站' }
]

export const REVIEW_LEVEL_GUIDE = [
  { level: 1, label: '班级', desc: '班级层面的活动或荣誉' },
  { level: 2, label: '系级', desc: '系/专业层面的活动或荣誉' },
  { level: 3, label: '院级', desc: '学院层面的活动或荣誉' },
  { level: 4, label: '校级', desc: '学校层面的活动或荣誉' },
  { level: 5, label: '市级', desc: '市级及以上的活动或荣誉' }
]

export const GROWTH_DIMENSIONS = [
  {
    key: 'academic', label: '学业发展', icon: '📖', color: '#3498DB',
    subcategories: [
      { key: 'course', label: '课程成绩' },
      { key: 'research', label: '学术项目' },
      { key: 'competition', label: '竞赛获奖' },
      { key: 'certificate', label: '证书考取' }
    ]
  },
  {
    key: 'practice', label: '能力实践', icon: '🔧', color: '#2ECC71',
    subcategories: [
      { key: 'club', label: '社团活动' },
      { key: 'volunteer', label: '志愿服务' },
      { key: 'internship', label: '实习实践' },
      { key: 'skill', label: '技能培训' }
    ]
  },
  {
    key: 'inner', label: '内在成长', icon: '🌱', color: '#9B59B6',
    subcategories: [
      { key: 'goal', label: '目标规划' },
      { key: 'reflect', label: '反思笔记' },
      { key: 'mentor', label: '导生谈心' },
      { key: 'highlight', label: '高光时刻' }
    ]
  }
]

export const POST_STATUS = {
  PENDING: 'pending',
  PUBLISHED: 'published',
  REVIEW: 'review',
  ARCHIVED: 'archived'
}

export const POST_STATUS_LABELS = {
  pending: '待审核', published: '已发布', review: '复审中',
  archived: '已封存', flagged: '违规', pinned: '置顶'
}

export const USER_ROLES = { USER: 'user', ADMIN: 'admin' }

export const POINTS_REASONS = {
  POST_PUBLISHED: 'post_published',
  ACHIEVEMENT_SUBMIT: 'achievement_submit',
  ACHIEVEMENT_APPROVED: 'achievement_approved',
  ACHIEVEMENT_UNLOCK: 'achievement_unlock',
  ADMIN_SCORE: 'admin_score',
  CREATE_ACCOUNT: 'create_account'
}

export const POINTS_REASON_LABELS = {
  post_published: '发布动态', achievement_submit: '提交成果',
  achievement_approved: '成果审核通过', achievement_unlock: '解锁成就',
  admin_score: '导生评分奖励', create_account: '创建角色'
}

export const AI_CONFIG = {
  API_KEY: '46feac02-aae8-44a4-8e1f-6f46fc8d64ae',
  API_URL: 'https://ark.cn-beijing.volces.com/api/v3/responses',
  MODEL: 'doubao-seed-2-0-pro-260215',
  SYSTEM_PROMPT: '你是"云迹"校园社交平台的 AI 助手，名叫"云小迹"。你友善、耐心、积极向上，擅长解答学习、校园生活、情感等方面的问题。请用简洁、亲切的语气回答用户的问题。如果涉及心理健康等敏感话题，请建议用户寻求专业帮助。',
  MAX_HISTORY: 20,
  MAX_INPUT_LENGTH: 1000
}

export const MODERATION_CONFIG = {
  MAX_CONTENT_LENGTH: 2000,
  MAX_IMAGES: 9,
  IMAGE_MAX_SIZE_MB: 10,
  MAX_COMMENT_LENGTH: 500
}

export const FEATURE_FLAGS = {
  ENABLE_ANONYMOUS_POST: true,
  ENABLE_ADMIN_NOTIFY: true,
  ENABLE_EMOTION_HELP: true,
  ENABLE_DAILY_LOGIN_POINTS: false,
  ENABLE_BATCH_OPERATIONS: true,
  ENABLE_PUSH_NOTIFICATION: false,
  ENABLE_POINTS_EXCHANGE: false
}

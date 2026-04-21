/**
 * 德智体美劳：各育预设活动说明与推荐蜕变等级（1～5）。
 * 「其他」自填标题并自选等级。
 */
import { GROWTH_OTHER_KEY, buildGrowthSubmitText } from './growthPresets.js'

export const VIRTUE_OTHER_KEY = GROWTH_OTHER_KEY

/** @typedef {{ text: string, level: number }} VirtuePresetLine */

/** @type {Record<string, VirtuePresetLine[]>} */
export const VIRTUE_PRESETS = {
  moral: [
    { text: '参与共青团先进个人 / 集体评选，向优秀榜样学习', level: 4 },
    { text: '参加十佳主题团日评选，展现团支部风采', level: 4 },
    { text: '参与活力团支部、魅力团支书评选，提升团务能力', level: 4 },
    { text: '参加主题升旗仪式，厚植爱国情怀', level: 3 },
    { text: '参与十佳团日评选，共建活力团支部', level: 4 },
    { text: '加入青年领袖计划，提升综合能力与思想觉悟', level: 4 },
    { text: '参评优秀学生 / 学生干部，争做优秀学子', level: 3 },
    { text: '参与宪法宣传周，学习法律知识、增强法治意识', level: 3 },
    { text: '参加国际志愿者日宪法游园，趣味学法律', level: 3 },
    { text: '参与党建品牌活动，了解基层社会治理', level: 3 },
  ],
  intellectual: [
    { text: '参加学术嘉年华，感受学术氛围、提升科研兴趣', level: 3 },
    { text: '参与师范生教学技能大赛，锻炼授课基本功', level: 4 },
    { text: '参加理论宣讲比赛，提升表达与理论素养', level: 3 },
    { text: '参与反诈宣讲比赛，学习防骗知识、提升安全意识', level: 3 },
    { text: '参加法援杯案例分析赛，锻炼法律逻辑与思辨力', level: 3 },
    { text: '观看 / 参与模拟法庭展演，体验真实司法流程', level: 3 },
    { text: '参加模拟法庭比赛，提升法律实践能力', level: 4 },
    { text: '听学涯启明分享会，学习科研竞赛经验', level: 2 },
    { text: '参与政青春社团课，关注社会热点、拓展视野', level: 2 },
    { text: '参加模拟政协社团课，了解政协知识与提案写作', level: 2 },
  ],
  physical: [
    { text: '参加新启杯羽毛球赛，运动健身、展现活力', level: 4 },
    { text: '参与校运会，为学院争光、锻炼体魄', level: 4 },
    { text: '参与宪法游园趣味运动，快乐运动强体质', level: 3 },
    { text: '参加社团文化季运动打卡，坚持日常锻炼', level: 3 },
    { text: '参与暑期职业训练营素质拓展，磨炼意志', level: 3 },
    { text: '参加青哲计划体能团建，提升团队协作力', level: 3 },
    { text: '参与团学干部户外拓展，增强体能与凝聚力', level: 3 },
    { text: '参加班级体育活动，养成运动好习惯', level: 1 },
    { text: '参加主持人大赛，锻炼口才、提升舞台表现力', level: 4 },
  ],
  aesthetic: [
    { text: '参与青春盛典，感受校园文化、展示风采', level: 4 },
    { text: '参加 PPT 模板大赛，提升审美与办公技能', level: 3 },
    { text: '体验漆韵扇影手工活动，感受国风美学', level: 2 },
    { text: '参与非遗刺绣活动，了解传统工艺之美', level: 2 },
    { text: '学习中国结制作，感受非遗文化、动手创作', level: 2 },
  ],
  labor: [
    { text: '参加寒假社会实践，在实践中增长才干', level: 3 },
    { text: '参与暑期社会实践，服务社会、提升能力', level: 3 },
    { text: '参加春季圆梦蒲公英，志愿帮扶青少年', level: 3 },
    { text: '参加秋季圆梦蒲公英，持续开展爱心帮扶', level: 3 },
    { text: '参与社区为老服务，奉献爱心、践行志愿精神', level: 3 },
    { text: '参加禁毒宣讲志愿活动，传递健康生活理念', level: 3 },
  ],
}

export function getVirtuePresets(categoryKey) {
  return VIRTUE_PRESETS[categoryKey] || []
}

export { buildGrowthSubmitText as buildVirtueSubmitText }

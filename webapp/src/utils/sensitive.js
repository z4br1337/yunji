/**
 * 本地敏感词检测（发帖前）。字母缩写类词条按「非字母数字边界」匹配，大小写不敏感。
 */
const ABBREV_WORDS = [
  'sb', 'nmb', 'nmd', 'nm', 'cnm', 'cn', 'md', 'tmd', 'tm', 'wcnm', 'rnm', 'mmp', 'mlgb',
  'nc', 'zz', 'bt', 'sjb', 'dsb', 'ds', 'sm', 'gzz'
]

const WORD_LISTS = {
  profanity: [
    '他妈', '你妈', '卧槽', '操你', '草你', '傻逼', '傻比', '煞笔', '沙比', '妈逼', '牛逼', '装逼', '逼的',
    '狗日', '日你', '滚蛋', '去死', '贱人', '婊子', '混蛋', '王八蛋', '废物', '白痴', '蠢货',
    '草', '操', '曹', '尼玛', '泥马', '卧草', '卧槽', '妈卖批', '特么', '脑残', '智障', '弱智',
    '傻子', '变态', '神经病', '疯子', '屌丝', '丑逼', '肥猪', '滚开', '滚粗', '杂种',
    '畜生', '恶心', '滚', '傻缺', '缺德', '狗东西', '泼妇', '怂货', '窝囊废', '脑残粉',
    '智障儿', '去死吧', '滚远点', '神经病啊', '变态狂', '弱智儿', 'fuck', 'shit', 'damn', 'bitch', 'ass'
  ],
  fraud: [
    '代课', '代跑', '替课', '替跑', '代签到', '代点名', '替考', '代考', '代写', '代做', '枪手', '找人代',
    '有偿代', '刷课', '挂课', '买答案', '卖答案', '论文代写', '代挂', '帮跑', '帮签',
    '兼职', '刷单', '返利', '下注', '赌博', '彩票', '贷款', '套现', '银行卡', '转账',
    '加微信', '加qq', '私聊我', '带你赚钱', '内幕', '高薪兼职', '日赚', '轻松月入', '校园贷', '高利贷',
    '借条', '网贷', '传销', '拉人头', '下线', '躺赚', '兼职刷'
  ],
  contraband: [
    '违规电器', '大功率电器', '电热毯', '热得快', '电炉', '电热锅', '电磁炉', '取暖器', '小太阳',
    '烟', '香烟', '电子烟', '打火机', '赌钱', '网赌',
    '毒品', '吸毒', '冰毒', '大麻', '摇头丸', '走私', '军火', '枪支', '弹药'
  ],
  danger: [
    '自杀', '自残', '割腕', '跳楼', '不想活', '打架', '群殴', '斗殴', '约架',
    '砍人', '弄死', '炸死', '绑架', '报复'
  ],
  discrimination: [
    '河南偷', '东北黑', '广东黑', '黑人', '支那', '歧视', '滚出'
  ],
  adult: [
    '约炮', '嫖娼', '一夜情', '按摩', '特殊服务', '裸聊', '下体', '精液', '妓女', '嫖客', '私聊'
  ],
  spam: ['代购', '微商', '包邮', '秒杀', '福利', '链接', '扫码', '造谣', '抹黑'],
  political: ['反动', '分裂', '独立', '港独', '台独', '疆独', '藏独'],
  toxic_game: ['菜鸡', '坑货', '孤儿', '送人头', '开挂', '脚本', '作弊'],
  cheating: ['抄袭', '作弊']
}

const CATEGORY_LABELS = {
  profanity: '脏话/辱骂',
  fraud: '诈骗/非法兼职',
  contraband: '违禁品/毒品枪支',
  danger: '暴力/危险行为',
  discrimination: '歧视/地域攻击',
  adult: '低俗/招嫖',
  spam: '营销/谣言',
  political: '敏感政治表述',
  toxic_game: '游戏辱骂',
  cheating: '抄袭作弊'
}

let _allWords = []
let _categoryMap = {}

function _init() {
  if (_allWords.length) return
  for (const cat in WORD_LISTS) {
    for (const w of WORD_LISTS[cat]) {
      const lw = w.toLowerCase()
      _allWords.push(lw)
      _categoryMap[lw] = cat
    }
  }
  _allWords.sort((a, b) => b.length - a.length)
}

function normalize(text) {
  if (!text) return ''
  let s = text.toLowerCase()
  s = s.replace(/[\s\u200b\u200c\u200d\ufeff]/g, '')
  s = s.replace(/[·.。,，、!！?？~～*#@＠]/g, '')
  s = s.replace(/0/g, 'o').replace(/1/g, 'i').replace(/3/g, 'e').replace(/4/g, 'a').replace(/5/g, 's')
  return s
}

function abbrevMatches(text, w) {
  const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp(`(?:^|[^a-z0-9])${escaped}(?:[^a-z0-9]|$)`, 'i').test(text)
}

export function check(text) {
  _init()
  if (!text || !text.trim()) return { pass: true, words: [], categories: [], highlighted: text || '' }
  const norm = normalize(text)
  const lower = text.toLowerCase()
  const matched = []
  const cats = {}

  for (const w of ABBREV_WORDS) {
    if (abbrevMatches(text, w) && !matched.includes(w)) {
      matched.push(w)
      cats.profanity = true
    }
  }

  for (const w of _allWords) {
    if ((norm.includes(w) || lower.includes(w)) && !matched.includes(w)) {
      matched.push(w)
      cats[_categoryMap[w]] = true
    }
  }

  let highlighted = text
  for (const w of matched) {
    if (/^[a-z0-9]+$/i.test(w) && w.length <= 4) {
      const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      highlighted = highlighted.replace(
        new RegExp(`(^|[^a-zA-Z0-9])(${escaped})([^a-zA-Z0-9]|$)`, 'gi'),
        '$1<mark>$2</mark>$3'
      )
    } else {
      highlighted = highlighted.replace(
        new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'),
        `<mark>${w}</mark>`
      )
    }
  }
  return { pass: !matched.length, words: matched, categories: Object.keys(cats), highlighted }
}

export function getCategoryLabel(cat) {
  return CATEGORY_LABELS[cat] || cat
}

const WORD_LISTS = {
  profanity: ['他妈','你妈','卧槽','操你','草你','傻逼','煞笔','沙比','妈逼','牛逼','装逼','逼的','狗日','日你','滚蛋','去死','贱人','婊子','混蛋','王八蛋','废物','白痴','蠢货','fuck','shit','damn','bitch','ass'],
  cheating: ['代课','代跑','替课','替跑','代签到','代点名','替考','代考','代写','代做','枪手','找人代','帮忙代','有偿代','刷课','挂课','买答案','卖答案','作弊','抄袭','论文代写','代挂','帮跑','帮签'],
  contraband: ['违规电器','大功率电器','电热毯','热得快','电炉','电热锅','电磁炉','取暖器','小太阳','烟','香烟','电子烟','打火机','赌博','赌钱','网赌','彩票','下注'],
  fraud: ['刷单','兼职刷','高薪兼职','日赚','轻松月入','贷款','校园贷','高利贷','借条','网贷','传销','拉人头','下线','返利','躺赚'],
  danger: ['自杀','自残','割腕','跳楼','不想活','打架','群殴','斗殴','约架']
}

const CATEGORY_LABELS = {
  profanity: '脏话/辱骂', cheating: '代课/作弊',
  contraband: '违禁品/违规电器', fraud: '诈骗/非法兼职', danger: '危险行为'
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

export function check(text) {
  _init()
  if (!text || !text.trim()) return { pass: true, words: [], categories: [], highlighted: text || '' }
  const norm = normalize(text)
  const lower = text.toLowerCase()
  const matched = [], cats = {}
  for (const w of _allWords) {
    if ((norm.includes(w) || lower.includes(w)) && !matched.includes(w)) {
      matched.push(w)
      cats[_categoryMap[w]] = true
    }
  }
  let highlighted = text
  for (const w of matched) highlighted = highlighted.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), `<mark>${w}</mark>`)
  return { pass: !matched.length, words: matched, categories: Object.keys(cats), highlighted }
}

export function getCategoryLabel(cat) { return CATEGORY_LABELS[cat] || cat }

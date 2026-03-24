"""与 webapp/src/utils/sensitive.js 对齐的敏感词检测（服务端发帖校验）。"""
import re

ABBREV_WORDS = [
    'sb', 'nmb', 'nmd', 'nm', 'cnm', 'cn', 'md', 'tmd', 'tm', 'wcnm', 'rnm', 'mmp', 'mlgb',
    'nc', 'zz', 'bt', 'sjb', 'dsb', 'ds', 'sm', 'gzz',
]

WORD_LISTS = {
    'profanity': [
        '他妈', '你妈', '卧槽', '操你', '草你', '傻逼', '傻比', '煞笔', '沙比', '妈逼', '牛逼', '装逼', '逼的',
        '狗日', '日你', '滚蛋', '去死', '贱人', '婊子', '混蛋', '王八蛋', '废物', '白痴', '蠢货',
        '草', '操', '曹', '尼玛', '泥马', '卧草', '卧槽', '妈卖批', '特么', '脑残', '智障', '弱智',
        '傻子', '变态', '神经病', '疯子', '屌丝', '丑逼', '肥猪', '滚开', '滚粗', '杂种',
        '畜生', '恶心', '滚', '傻缺', '缺德', '狗东西', '泼妇', '怂货', '窝囊废', '脑残粉',
        '智障儿', '去死吧', '滚远点', '神经病啊', '变态狂', '弱智儿', 'fuck', 'shit', 'damn', 'bitch', 'ass',
    ],
    'fraud': [
        '代课', '代跑', '替课', '替跑', '代签到', '代点名', '替考', '代考', '代写', '代做', '枪手', '找人代',
        '有偿代', '刷课', '挂课', '买答案', '卖答案', '论文代写', '代挂', '帮跑', '帮签',
        '兼职', '刷单', '返利', '下注', '赌博', '彩票', '贷款', '套现', '银行卡', '转账',
        '加微信', '加qq', '私聊我', '带你赚钱', '内幕', '高薪兼职', '日赚', '轻松月入', '校园贷', '高利贷',
        '借条', '网贷', '传销', '拉人头', '下线', '躺赚', '兼职刷',
    ],
    'contraband': [
        '违规电器', '大功率电器', '电热毯', '热得快', '电炉', '电热锅', '电磁炉', '取暖器', '小太阳',
        '烟', '香烟', '电子烟', '打火机', '赌钱', '网赌',
        '毒品', '吸毒', '冰毒', '大麻', '摇头丸', '走私', '军火', '枪支', '弹药',
    ],
    'danger': [
        '自杀', '自残', '割腕', '跳楼', '不想活', '打架', '群殴', '斗殴', '约架',
        '砍人', '弄死', '炸死', '绑架', '报复',
    ],
    'discrimination': ['河南偷', '东北黑', '广东黑', '黑人', '支那', '歧视', '滚出'],
    'adult': [
        '约炮', '嫖娼', '一夜情', '按摩', '特殊服务', '裸聊', '下体', '精液', '妓女', '嫖客', '私聊',
    ],
    'spam': ['代购', '微商', '包邮', '秒杀', '福利', '链接', '扫码', '造谣', '抹黑'],
    'political': ['反动', '分裂', '独立', '港独', '台独', '疆独', '藏独'],
    'toxic_game': ['菜鸡', '坑货', '孤儿', '送人头', '开挂', '脚本', '作弊'],
    'cheating': ['抄袭', '作弊'],
}

_all_words_sorted = None
_category_map = None


def _ensure_init():
    global _all_words_sorted, _category_map
    if _all_words_sorted is not None:
        return
    _category_map = {}
    flat = []
    for cat, words in WORD_LISTS.items():
        for w in words:
            lw = w.lower()
            flat.append(lw)
            _category_map[lw] = cat
    _all_words_sorted = sorted(set(flat), key=len, reverse=True)


def normalize(text):
    if not text:
        return ''
    s = text.lower()
    s = re.sub(r'[\s\u200b\u200c\u200d\ufeff]', '', s)
    s = re.sub(r'[·.。,，、!！?？~～*#@＠]', '', s)
    s = s.replace('0', 'o').replace('1', 'i').replace('3', 'e').replace('4', 'a').replace('5', 's')
    return s


def abbrev_matches(text, w):
    escaped = re.escape(w)
    return re.search(r'(?:^|[^a-z0-9])' + escaped + r'(?:[^a-z0-9]|$)', text, re.I) is not None


def check(text):
    """返回 (是否通过, 命中词列表)。"""
    _ensure_init()
    if not text or not str(text).strip():
        return True, []
    text = str(text)
    norm = normalize(text)
    lower = text.lower()
    matched = []

    for w in ABBREV_WORDS:
        if abbrev_matches(text, w) and w not in matched:
            matched.append(w)

    for w in _all_words_sorted:
        if w in matched:
            continue
        if w in norm or w in lower:
            matched.append(w)

    return len(matched) == 0, matched


def content_passes(text):
    ok, _ = check(text)
    return ok

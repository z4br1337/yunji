# 可选班级（与前端 schoolClasses 保持一致）
ALLOWED_CLASSES = frozenset([
    '25行管1班',
    '25行管2班',
    '25人资1班',
    '25人资2班',
    '25法学1班',
    '25法学2班',
    '25哲学1班',
    '25社保1班',
    '25思政道法1班',
    '25社工1班',
])


def is_allowed_class(value):
    if not value or not isinstance(value, str):
        return False
    return value.strip() in ALLOWED_CLASSES


# 最高管理员账号（不对外展示专属称号，仅后端鉴权）
SUPER_ADMIN_USERNAME = 'daoshengzsb0125'
# 绑定以下学号的账号与上述账号同等最高权限
SUPER_ADMIN_STUDENT_IDS = frozenset({'240153287'})


def is_super_admin_user(user):
    if not user:
        return False
    if (getattr(user, 'username', None) or '').strip() == SUPER_ADMIN_USERNAME:
        return True
    sid = (getattr(user, 'student_id', None) or '').strip()
    if sid and sid in SUPER_ADMIN_STUDENT_IDS:
        return True
    return False

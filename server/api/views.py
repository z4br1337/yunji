"""
云迹 Django 后端视图
所有接口统一返回格式: { "code": 0, "message": "ok", "data": { ... } }
鉴权: Authorization: Bearer <token>
"""
import json
import os
import uuid
import time
import hashlib
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import models as db_models
from django.db.models import Q, F, Count, Max, Exists, OuterRef
from django.db.models.functions import Greatest
from django.conf import settings
from django.utils import timezone

from .constants import ALLOWED_CLASSES, is_allowed_class, is_super_admin_user
from . import sensitive_check
from .models import (
    User, Post, Comment, Achievement, Invite, PointsLog, Message, FileShare,
    ShopItem, ExchangeRecord, AdminActionLog,
)

_STUDENT_ID_RE = re.compile(r'^[A-Za-z0-9_-]{4,32}$')

EXP_PER_POST = 10
EXP_TO_SCORE_RATIO = 5  # 每5经验值=1积分
ACHIEVEMENT_BASE_EXP = 500
ACHIEVEMENT_LEVEL_MULTIPLIER = 500
ACHIEVEMENT_MAX_EXP = 2500
PAGE_SIZE = 20


def _log_admin_action(admin, action, target_type, target_id, detail):
    AdminActionLog.objects.create(
        admin_id=admin.openid,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        detail=detail or {},
    )


def _admin_class_err(admin):
    if is_super_admin_user(admin):
        return None
    if not is_allowed_class(admin.user_class):
        return err('PROFILE_INCOMPLETE', '请先在「我的」完善资料并选择班级')
    return None


def _admin_class_value(admin):
    return (admin.user_class or '').strip()


def _user_in_admin_class(admin, author_openid):
    if is_super_admin_user(admin):
        return True
    ac = _admin_class_value(admin)
    if not is_allowed_class(ac):
        return False
    try:
        u = User.objects.get(openid=author_openid)
        return (u.user_class or '').strip() == ac
    except User.DoesNotExist:
        return False


def _ensure_post_admin_scope(admin, post_id):
    e = _admin_class_err(admin)
    if e:
        return None, e
    try:
        pid = int(post_id)
        p = Post.objects.get(id=pid)
    except (Post.DoesNotExist, ValueError, TypeError):
        return None, err('NOT_FOUND', '帖子不存在')
    if not _user_in_admin_class(admin, p.author_id):
        return None, err('FORBIDDEN', '无权操作其他班级的帖子')
    return p, None


def ok(data=None, message='ok'):
    return JsonResponse({'code': 0, 'message': message, 'data': data or {}})


def err(code, message):
    return JsonResponse({'code': code, 'message': message, 'data': {}})


def get_body(request):
    try:
        return json.loads(request.body) if request.body else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def get_or_create_user(openid):
    user, created = User.objects.get_or_create(
        openid=openid,
        defaults={'exp': 10, 'score': 10 // EXP_TO_SCORE_RATIO, 'achievement_counts': {}}
    )
    return user


def require_admin(user):
    return user.role == 'admin'


def user_to_dict(u, post_count_exclude_emotion=False):
    post_count = u.post_count
    if post_count_exclude_emotion:
        post_count = Post.objects.filter(author_id=u.openid).exclude(category='emotion').count()
    return {
        '_id': u.openid,
        'username': u.username or '',
        'nickname': u.nickname, 'class': u.user_class,
        'avatarUrl': u.avatar_url,
        'profileCompleted': u.profile_completed,
        'role': u.role, 'exp': u.exp, 'score': u.score,
        'postCount': post_count,
        'achievementCounts': u.achievement_counts or {},
        'growthBookPublic': u.growth_book_public,
        'inviteUsed': u.invite_used,
        'email': (u.email or '').strip(),
        'studentId': (u.student_id or '').strip(),
        'isSuperAdmin': is_super_admin_user(u),
        'createdAt': u.created_at.isoformat() if u.created_at else '',
        'updatedAt': u.updated_at.isoformat() if u.updated_at else '',
    }


def post_to_dict(p, reveal_author=False):
    d = {
        '_id': str(p.id), 'authorId': p.author_id,
        'isAnonymous': p.is_anonymous,
        'visibleAuthorName': p.visible_author_name,
        'content': p.content, 'images': p.images or [],
        'category': p.category, 'status': p.status,
        'pinned': p.pinned, 'pointsAwarded': p.points_awarded,
        'notifyAdmin': p.notify_admin,
        'needOffline': p.need_offline,
        'offlineTime': p.offline_time, 'offlinePlace': p.offline_place,
        'flagged': p.flagged, 'flaggedWords': p.flagged_words or [],
        'flaggedCategories': p.flagged_categories or [],
        'flaggedHighlighted': p.flagged_highlighted,
        'createdAt': p.created_at.isoformat() if p.created_at else '',
        'updatedAt': p.updated_at.isoformat() if p.updated_at else '',
    }
    try:
        author = User.objects.get(openid=p.author_id)
        d['authorAvatarUrl'] = author.avatar_url or ''
        if reveal_author:
            d['authorName'] = author.nickname
            d['authorClass'] = author.user_class
    except User.DoesNotExist:
        d['authorAvatarUrl'] = ''
        if reveal_author:
            d['authorName'] = '未知'
            d['authorClass'] = ''
    return d


def _user_avatar_url(openid):
    try:
        u = User.objects.get(openid=openid)
        return u.avatar_url or ''
    except User.DoesNotExist:
        return ''


def _comment_to_json(c):
    par = c.parent_comment if getattr(c, 'parent_comment_id', None) else None
    return {
        '_id': str(c.id), 'postId': str(c.post_id), 'authorId': c.author_id,
        'authorName': c.author_name, 'isAdmin': c.is_admin, 'content': c.content,
        'parentCommentId': str(par.id) if par else '',
        'parentAuthorName': par.author_name if par else '',
        'createdAt': c.created_at.isoformat() if c.created_at else '',
    }


def ach_to_dict(a, include_author=False):
    d = {
        '_id': str(a.id), 'userId': a.user_id,
        'title': a.title, 'description': a.description,
        'category': a.category, 'dimension': a.dimension,
        'subcategory': a.subcategory, 'level': a.level,
        'points': a.points, 'expAwarded': a.exp_awarded,
        'images': a.images or [], 'status': a.status,
        'createdAt': a.created_at.isoformat() if a.created_at else '',
    }
    if include_author:
        u = getattr(a, 'user', None)
        if u is not None:
            d['authorNickname'] = u.nickname or ''
            d['authorClass'] = u.user_class or ''
    return d


# ======================== 密码工具 ========================

def _hash_password(password):
    salt = os.environ.get('PASSWORD_SALT', 'yunji_salt_2026')
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()


def _normalize_student_id(sid):
    return (sid or '').strip()


def _validate_student_id(sid):
    return bool(sid and _STUDENT_ID_RE.match(sid))


# ======================== 用户 ========================

@csrf_exempt
@require_POST
def user_register(request):
    body = get_body(request)
    username = (body.get('username') or '').strip()
    password = (body.get('password') or '').strip()
    nickname = (body.get('nickname') or '').strip()

    if not username or not password or not nickname:
        return err('INVALID_PARAMS', '昵称、账号、密码均为必填')
    if len(username) < 3 or len(username) > 32:
        return err('INVALID_PARAMS', '账号长度需在 3~32 位之间')
    if len(password) < 6:
        return err('INVALID_PARAMS', '密码长度至少 6 位')
    if len(nickname) > 20:
        return err('INVALID_PARAMS', '昵称最多 20 个字符')

    if User.objects.filter(username=username).exists():
        return err('USERNAME_EXISTS', '该账号已被注册')

    openid = uuid.uuid4().hex[:24]
    user = User.objects.create(
        openid=openid,
        username=username,
        password_hash=_hash_password(password),
        nickname=nickname,
        profile_completed=False,
        exp=10, score=10 // EXP_TO_SCORE_RATIO, achievement_counts={},
    )
    return ok({
        'user': user_to_dict(user, post_count_exclude_emotion=True),
        'token': openid,
    })


@csrf_exempt
@require_POST
def user_login(request):
    body = get_body(request)
    identifier = (body.get('username') or '').strip()
    password = (body.get('password') or '').strip()

    if identifier and password:
        ph = _hash_password(password)
        users = []
        try:
            u = User.objects.get(username=identifier)
            users = [u]
        except User.DoesNotExist:
            sid = _normalize_student_id(identifier)
            if sid and _validate_student_id(sid):
                users = list(User.objects.filter(student_id=sid))
        if not users:
            return err('USER_NOT_FOUND', '账号不存在')
        matching = [u for u in users if u.password_hash == ph]
        if not matching:
            return err('WRONG_PASSWORD', '密码错误')
        if len(matching) > 1:
            return JsonResponse({
                'code': 'PICK_ACCOUNT',
                'message': '该学号绑定了多个账号，请选择要登录的账号',
                'data': {
                    'accounts': [{
                        'username': u.username or '',
                        'nickname': u.nickname or '',
                        'avatarUrl': u.avatar_url or '',
                    } for u in matching],
                },
            })
        user = matching[0]
        if is_super_admin_user(user) and user.role != 'admin':
            user.role = 'admin'
            user.save(update_fields=['role'])
        return ok({
            'user': user_to_dict(user, post_count_exclude_emotion=True),
            'token': user.openid,
            'profileCompleted': user.profile_completed,
        })

    token = request.user_token
    if not token:
        return err('UNAUTHORIZED', '请先登录')
    user = get_or_create_user(token)
    return ok({
        'user': user_to_dict(user, post_count_exclude_emotion=True),
        'token': user.openid,
        'profileCompleted': user.profile_completed,
    })


@csrf_exempt
@require_POST
def user_profile(request):
    openid = request.user_token
    if not openid:
        return err('UNAUTHORIZED', '无法获取用户身份')
    user = get_or_create_user(openid)
    body = get_body(request)

    nickname = body.get('nickname')
    user_class = body.get('class')
    growth_book_public = body.get('growthBookPublic')
    avatar_url = body.get('avatarUrl')

    if nickname is not None:
        user.nickname = nickname
    if user_class is not None:
        ucls = (user_class or '').strip()
        if ucls and not is_allowed_class(ucls):
            return err('INVALID_PARAMS', '请从列表中选择合法班级')
        user.user_class = ucls
    if growth_book_public is not None:
        user.growth_book_public = bool(growth_book_public)
    if avatar_url is not None:
        user.avatar_url = avatar_url

    user.profile_completed = bool(
        (user.nickname or '').strip() and is_allowed_class(user.user_class)
    )

    user.save()
    return ok({'user': user_to_dict(user, post_count_exclude_emotion=True), 'profileCompleted': user.profile_completed})


@csrf_exempt
@require_POST
def user_change_password(request):
    openid = request.user_token
    if not openid:
        return err('UNAUTHORIZED', '请先登录')

    body = get_body(request)
    old_password = (body.get('oldPassword') or '').strip()
    new_password = (body.get('newPassword') or '').strip()

    if not old_password or not new_password:
        return err('INVALID_PARAMS', '旧密码和新密码不能为空')
    if len(new_password) < 6:
        return err('INVALID_PARAMS', '新密码长度至少 6 位')
    if old_password == new_password:
        return err('INVALID_PARAMS', '新密码不能与旧密码相同')

    try:
        user = User.objects.get(openid=openid)
    except User.DoesNotExist:
        return err('USER_NOT_FOUND', '用户不存在')

    if not user.password_hash or user.password_hash != _hash_password(old_password):
        return err('WRONG_PASSWORD', '旧密码错误')

    user.password_hash = _hash_password(new_password)
    user.save(update_fields=['password_hash', 'updated_at'])
    return ok({'changed': True})


@csrf_exempt
@require_POST
def bind_student_id(request):
    openid = request.user_token
    if not openid:
        return err('UNAUTHORIZED', '请先登录')
    body = get_body(request)
    sid = _normalize_student_id(body.get('studentId') or '')
    if not _validate_student_id(sid):
        return err('INVALID_PARAMS', '学号须为 4～32 位字母、数字、下划线或短横线')
    try:
        user = User.objects.get(openid=openid)
    except User.DoesNotExist:
        return err('USER_NOT_FOUND', '用户不存在')
    if (user.student_id or '').strip():
        return err('ALREADY_BOUND', '已绑定学号')
    user.student_id = sid
    user.save(update_fields=['student_id', 'updated_at'])
    return ok({'user': user_to_dict(user, post_count_exclude_emotion=True)})


@csrf_exempt
@require_POST
def use_invite_code(request):
    openid = request.user_token
    body = get_body(request)
    code = body.get('code', '').strip()
    if not code:
        return err('INVALID_PARAMS', '请输入邀请码')

    try:
        invite = Invite.objects.get(code=code)
    except Invite.DoesNotExist:
        return err('INVITE_INVALID', '邀请码无效')

    if invite.used_by:
        return err('INVITE_USED', '邀请码已被使用')

    invite.used_by = openid
    invite.save()

    user = get_or_create_user(openid)
    user.role = 'admin'
    user.invite_used = code
    user.save()
    return ok({'role': 'admin'})


@csrf_exempt
@require_POST
def user_points_log(request):
    openid = request.user_token
    logs = PointsLog.objects.filter(user_id=openid)[:30]
    return ok({'logs': [{
        '_id': str(l.id), 'userId': l.user_id, 'delta': l.delta,
        'type': l.log_type, 'reason': l.reason, 'relatedId': l.related_id,
        'createdAt': l.created_at.isoformat() if l.created_at else '',
    } for l in logs]})


# ======================== 帖子 ========================

@csrf_exempt
@require_POST
def post_create(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    if not user.profile_completed:
        return err('PROFILE_INCOMPLETE', '请先完善个人资料')

    body = get_body(request)
    content = (body.get('content') or '').strip()
    if not sensitive_check.content_passes(content):
        return err('SENSITIVE_CONTENT', '内容包含敏感词，无法发布')

    p = Post.objects.create(
        author_id=openid,
        is_anonymous=bool(body.get('isAnonymous')),
        visible_author_name='匿名用户' if body.get('isAnonymous') else user.nickname,
        content=body.get('content', ''),
        images=body.get('images', []),
        category=body.get('category', 'cognition'),
        status='published',
        notify_admin=bool(body.get('notifyAdminFlag')),
        need_offline=bool(body.get('needOffline')),
        offline_time=body.get('offlineTime', ''),
        offline_place=body.get('offlinePlace', ''),
        flagged=False,
        flagged_words=[],
        flagged_categories=[],
        flagged_highlighted='',
    )

    exp_gain = EXP_PER_POST
    score_gain = exp_gain // EXP_TO_SCORE_RATIO
    User.objects.filter(openid=openid).update(
        exp=F('exp') + exp_gain,
        score=F('score') + score_gain,
        post_count=F('post_count') + 1,
    )
    PointsLog.objects.create(
        user_id=openid, delta=exp_gain, log_type='exp',
        reason='post_published', related_id=str(p.id),
    )

    return ok({'postId': str(p.id), 'expGain': exp_gain})


@csrf_exempt
@require_POST
def post_delete(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    body = get_body(request)
    try:
        pid = int(body.get('postId'))
    except (TypeError, ValueError):
        return err('INVALID_PARAMS', '帖子ID无效')
    try:
        p = Post.objects.get(id=pid)
    except Post.DoesNotExist:
        return err('NOT_FOUND', '帖子不存在')

    if p.author_id == openid:
        pass
    elif user.role == 'admin':
        e2 = _admin_class_err(user)
        if e2:
            return e2
        if not _user_in_admin_class(user, p.author_id):
            return err('FORBIDDEN', '无权删除其他班级的帖子')
    else:
        return err('FORBIDDEN', '无权删除该帖子')

    author_openid = p.author_id
    should_decr = (p.status in ('published', 'archived')) and not p.flagged
    summary = (p.content or '')[:120]
    cat = p.category
    p.delete()
    if should_decr:
        User.objects.filter(openid=author_openid).update(
            post_count=Greatest(F('post_count') - 1, 0)
        )
    if user.role == 'admin' and user.openid != author_openid:
        try:
            au = User.objects.get(openid=author_openid)
            _log_admin_action(user, 'post_delete', 'post', pid, {
                'summary': summary,
                'category': cat,
                'authorNickname': au.nickname,
                'authorClass': au.user_class or '',
            })
        except User.DoesNotExist:
            _log_admin_action(user, 'post_delete', 'post', pid, {'summary': summary, 'category': cat})
    return ok({})


@csrf_exempt
@require_POST
def post_list(request):
    openid = request.user_token
    body = get_body(request)
    f = body.get('filter', {})
    page = max(int(body.get('page', 1)), 1)
    req_page_size = int(body.get('pageSize', PAGE_SIZE))
    page_size = min(max(req_page_size, 5), 30)

    user = get_or_create_user(openid)
    is_admin = user.role == 'admin'
    qs = Post.objects.all()

    if f.get('_id'):
        qs = qs.filter(id=int(f['_id']))
    elif f.get('myPosts'):
        qs = qs.filter(author_id=openid)
        if f.get('excludeEmotion'):
            qs = qs.exclude(category='emotion')
        if f.get('status'):
            qs = qs.filter(status=f['status'])
    else:
        if f.get('status') == 'flagged':
            qs = qs.filter(status='flagged')
        else:
            if not is_admin:
                qs = qs.exclude(status='flagged').exclude(status='archived')
            if f.get('excludeEmotion'):
                qs = qs.exclude(category='emotion')
            if f.get('category') == 'emotion':
                qs = qs.filter(category='emotion')
                if not is_admin:
                    qs = qs.filter(author_id=openid)
            elif f.get('category'):
                qs = qs.filter(category=f['category']).exclude(category='emotion')
            if f.get('status') and f['status'] != 'flagged':
                qs = qs.filter(status=f['status'])
            if not is_admin:
                qs = qs.filter(Q(status='published') | Q(author_id=openid))

    search_kw = (f.get('keyword') or f.get('search') or '').strip()
    if search_kw:
        qs = qs.filter(content__icontains=search_kw)

    total = qs.count()
    start = (page - 1) * page_size
    posts = qs[start:start + page_size]
    return ok({
        'posts': [post_to_dict(p, reveal_author=is_admin) for p in posts],
        'total': total,
        'hasMore': start + page_size < total,
    })


@csrf_exempt
@require_POST
def post_detail(request):
    body = get_body(request)
    post_id = body.get('postId')
    try:
        p = Post.objects.get(id=int(post_id))
    except (Post.DoesNotExist, ValueError, TypeError):
        return err('NOT_FOUND', '帖子不存在')
    openid = request.user_token
    user = get_or_create_user(openid)
    if p.category == 'emotion':
        if user.role == 'admin':
            if not _user_in_admin_class(user, p.author_id):
                return err('FORBIDDEN', '无权查看该情感倾诉')
        elif p.author_id != openid:
            return err('FORBIDDEN', '无权查看该情感倾诉')
    return ok({'posts': [post_to_dict(p, reveal_author=user.role == 'admin')], 'total': 1, 'hasMore': False})


# ======================== 评论 ========================

@csrf_exempt
@require_POST
def comment_add(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    body = get_body(request)
    try:
        p = Post.objects.get(id=int(body.get('postId')))
    except (Post.DoesNotExist, ValueError, TypeError):
        return err('NOT_FOUND', '帖子不存在')
    content = (body.get('content') or '').strip()
    if not content:
        return err('INVALID_PARAMS', '评论不能为空')
    if len(content) > 500:
        return err('INVALID_PARAMS', '评论过长')
    if not sensitive_check.content_passes(content):
        return err('SENSITIVE_CONTENT', '评论包含敏感词，无法发送')
    # 广场等非情感帖：任意用户（含各班级导生）均可评论；情感帖仅作者与同班导生等既有规则
    if user.role == 'admin' and p.category == 'emotion':
        e2 = _admin_class_err(user)
        if e2:
            return e2
        if not _user_in_admin_class(user, p.author_id):
            return err('FORBIDDEN', '无权评论该情感倾诉')
    parent = None
    raw_parent = body.get('parentCommentId') or body.get('replyToCommentId')
    if raw_parent:
        try:
            pid = int(raw_parent)
            parent = Comment.objects.get(id=pid, post_id=p.id)
        except (ValueError, TypeError, Comment.DoesNotExist):
            return err('INVALID_PARAMS', '回复的评论不存在')
    c = Comment.objects.create(
        post_id=p.id,
        parent_comment=parent,
        author_id=openid,
        author_name=user.nickname,
        is_admin=user.role == 'admin',
        content=content,
    )
    return ok({'commentId': str(c.id)})


@csrf_exempt
@require_POST
def comment_list(request):
    body = get_body(request)
    post_id = body.get('postId')
    try:
        p = Post.objects.get(id=int(post_id))
    except (Post.DoesNotExist, ValueError, TypeError):
        return err('NOT_FOUND', '帖子不存在')
    openid = request.user_token
    viewer = get_or_create_user(openid)
    if p.category == 'emotion':
        if viewer.role == 'admin':
            if not _user_in_admin_class(viewer, p.author_id):
                return err('FORBIDDEN', '无权查看')
        elif p.author_id != openid:
            return err('FORBIDDEN', '无权查看')
    comments = Comment.objects.filter(post_id=p.id).select_related('parent_comment').order_by('created_at')
    return ok({'comments': [_comment_to_json(c) for c in comments]})


@csrf_exempt
@require_POST
def comment_delete(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    body = get_body(request)
    try:
        cid = int(body.get('commentId'))
    except (TypeError, ValueError):
        return err('INVALID_PARAMS', '评论ID无效')
    try:
        c = Comment.objects.get(id=cid)
    except Comment.DoesNotExist:
        return err('NOT_FOUND', '评论不存在')
    try:
        p = Post.objects.get(id=c.post_id)
    except Post.DoesNotExist:
        c.delete()
        return ok({})

    if c.author_id == openid:
        c.delete()
        return ok({})
    if user.role != 'admin':
        return err('FORBIDDEN', '无权删除该评论')
    e2 = _admin_class_err(user)
    if e2:
        return e2
    if p.category == 'emotion' and not _user_in_admin_class(user, p.author_id):
        return err('FORBIDDEN', '无权删除该评论')
    c.delete()
    return ok({})


# ======================== 成果 ========================

@csrf_exempt
@require_POST
def achievement_create(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    if not user.profile_completed:
        return err('PROFILE_INCOMPLETE', '请先完善个人资料')

    body = get_body(request)
    images = body.get('images', [])
    if not images:
        return err('INVALID_PARAMS', '请上传证明照片')

    a = Achievement.objects.create(
        user_id=openid,
        title=body.get('title', '').strip(),
        description=body.get('description', '').strip(),
        category=body.get('category', ''),
        dimension=body.get('dimension', ''),
        subcategory=body.get('subcategory', ''),
        level=min(max(int(body.get('level', 1)), 1), 5),
        images=images,
        status='pending',
    )
    return ok({'achievementId': str(a.id), 'status': 'pending'})


@csrf_exempt
@require_POST
def achievement_list(request):
    openid = request.user_token
    body = get_body(request)
    if body.get('community'):
        qs = Achievement.objects.filter(
            status='approved',
            user__growth_book_public=True,
        ).select_related('user')
        if body.get('category'):
            qs = qs.filter(category=body['category'])
        achs = qs.order_by('-created_at')[:200]
        return ok({'achievements': [ach_to_dict(a, include_author=True) for a in achs]})
    qs = Achievement.objects.filter(user_id=body.get('userId') or openid)
    if body.get('category'):
        qs = qs.filter(category=body['category'])
    if body.get('status'):
        qs = qs.filter(status=body['status'])
    return ok({'achievements': [ach_to_dict(a) for a in qs]})


# ======================== 成长手册 ========================

@csrf_exempt
@require_POST
def growth_book_get(request):
    openid = request.user_token
    body = get_body(request)
    target_id = body.get('userId') or openid
    viewer = get_or_create_user(openid)
    is_owner = target_id == openid

    try:
        target = User.objects.get(openid=target_id)
    except User.DoesNotExist:
        return err('NOT_FOUND', '用户不存在')

    if not target.growth_book_public:
        if is_owner:
            pass
        elif viewer.role == 'admin' and (
            is_super_admin_user(viewer) or _user_in_admin_class(viewer, target_id)
        ):
            pass
        else:
            return err('PRIVATE', '该用户的成长手册未公开')

    achs = Achievement.objects.filter(user_id=target_id, status='approved')
    return ok({
        'achievements': [ach_to_dict(a) for a in achs],
        'user': user_to_dict(target),
        'isOwner': is_owner,
        'growthBookPublic': target.growth_book_public,
    })


@csrf_exempt
@require_POST
def growth_book_set_public(request):
    openid = request.user_token
    body = get_body(request)
    User.objects.filter(openid=openid).update(growth_book_public=bool(body.get('isPublic')))
    return ok()


# ======================== 私信 ========================

@csrf_exempt
@require_POST
def message_send(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    body = get_body(request)
    msg = Message.objects.create(
        from_id=openid, from_name=user.nickname,
        to_id=body.get('toId', ''), content=body.get('content', ''),
    )
    return ok({'messageId': str(msg.id)})


@csrf_exempt
@require_POST
def message_conversations(request):
    openid = request.user_token
    msgs = Message.objects.filter(Q(from_id=openid) | Q(to_id=openid))

    conv_map = {}
    for m in msgs:
        peer = m.to_id if m.from_id == openid else m.from_id
        if peer not in conv_map or m.created_at > conv_map[peer]['time']:
            conv_map[peer] = {'content': m.content, 'time': m.created_at}

    convs = []
    for peer_id, info in conv_map.items():
        unread = Message.objects.filter(from_id=peer_id, to_id=openid, read=False).count()
        try:
            peer_user = User.objects.get(openid=peer_id)
            peer_name = peer_user.nickname
        except User.DoesNotExist:
            peer_name = '未知用户'
        convs.append({
            'peerId': peer_id, 'peerName': peer_name,
            'lastContent': info['content'],
            'lastTime': info['time'].isoformat(),
            'unreadCount': unread,
        })

    convs.sort(key=lambda c: c['lastTime'], reverse=True)
    return ok({'conversations': convs})


@csrf_exempt
@require_POST
def interaction_unread_summary(request):
    openid = request.user_token
    dm_unread = Message.objects.filter(to_id=openid, read=False).count()
    try:
        u = User.objects.get(openid=openid)
    except User.DoesNotExist:
        return ok({'dmUnread': dm_unread, 'replyUnread': 0, 'postCommentUnread': 0, 'total': dm_unread})
    reply_ts = u.interaction_reply_seen_at
    post_ts = u.interaction_post_comment_seen_at
    reply_unread = Comment.objects.filter(
        parent_comment__author_id=openid,
    ).exclude(author_id=openid).filter(created_at__gt=reply_ts).count()
    pc_unread = Comment.objects.filter(
        post__author_id=openid,
    ).exclude(author_id=openid).filter(created_at__gt=post_ts).count()
    return ok({
        'dmUnread': dm_unread,
        'replyUnread': reply_unread,
        'postCommentUnread': pc_unread,
        'total': dm_unread + reply_unread + pc_unread,
    })


@csrf_exempt
@require_POST
def interaction_mark_seen(request):
    openid = request.user_token
    body = get_body(request)
    scope = (body.get('scope') or 'all').strip()
    now = timezone.now()
    if scope in ('dm', 'all'):
        Message.objects.filter(to_id=openid, read=False).update(read=True)
    if scope in ('reply', 'all'):
        User.objects.filter(openid=openid).update(interaction_reply_seen_at=now)
    if scope in ('post_comment', 'all'):
        User.objects.filter(openid=openid).update(interaction_post_comment_seen_at=now)
    return ok({})


@csrf_exempt
@require_POST
def interaction_replies_to_me(request):
    openid = request.user_token
    qs = Comment.objects.filter(
        parent_comment__isnull=False,
        parent_comment__author_id=openid,
    ).exclude(author_id=openid).select_related('post', 'parent_comment').order_by('-created_at')[:80]
    items = []
    for c in qs:
        par = c.parent_comment
        items.append({
            'commentId': str(c.id),
            'fromId': c.author_id,
            'fromName': c.author_name,
            'fromAvatarUrl': _user_avatar_url(c.author_id),
            'replyContent': c.content,
            'parentContent': (par.content or '')[:200] if par else '',
            'postId': str(c.post_id),
            'postSnippet': (c.post.content or '')[:100],
            'createdAt': c.created_at.isoformat() if c.created_at else '',
        })
    return ok({'items': items})


@csrf_exempt
@require_POST
def interaction_comments_on_my_posts(request):
    openid = request.user_token
    qs = Comment.objects.filter(post__author_id=openid).exclude(author_id=openid).select_related(
        'post', 'parent_comment',
    ).order_by('-created_at')[:80]
    items = []
    for c in qs:
        par = c.parent_comment
        items.append({
            'commentId': str(c.id),
            'fromId': c.author_id,
            'fromName': c.author_name,
            'fromAvatarUrl': _user_avatar_url(c.author_id),
            'content': c.content,
            'parentAuthorName': par.author_name if par else '',
            'postId': str(c.post_id),
            'postSnippet': (c.post.content or '')[:100],
            'createdAt': c.created_at.isoformat() if c.created_at else '',
        })
    return ok({'items': items})


@csrf_exempt
@require_POST
def message_history(request):
    openid = request.user_token
    body = get_body(request)
    peer = body.get('peerId', '')

    msgs = Message.objects.filter(
        (Q(from_id=openid) & Q(to_id=peer)) | (Q(from_id=peer) & Q(to_id=openid))
    )
    Message.objects.filter(from_id=peer, to_id=openid, read=False).update(read=True)

    return ok({'messages': [{
        '_id': str(m.id), 'fromId': m.from_id, 'fromName': m.from_name,
        'toId': m.to_id, 'content': m.content, 'read': m.read,
        'createdAt': m.created_at.isoformat() if m.created_at else '',
    } for m in msgs]})


# ======================== 图片上传 ========================

@csrf_exempt
@require_POST
def upload_image(request):
    f = request.FILES.get('file')
    if not f:
        return err('INVALID_PARAMS', '未收到文件')

    ext = f.name.rsplit('.', 1)[-1] if '.' in f.name else 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'
    save_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    with open(save_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)

    url = f'{settings.MEDIA_URL}uploads/{filename}'
    return ok({'url': url})


@csrf_exempt
@require_POST
def upload_file(request):
    f = request.FILES.get('file')
    if not f:
        return err('INVALID_PARAMS', '未收到文件')
    max_size = 10 * 1024 * 1024  # 10MB
    if f.size > max_size:
        return err('INVALID_PARAMS', '文件大小不能超过10MB')
    ext = f.name.rsplit('.', 1)[-1] if '.' in f.name else 'bin'
    filename = f'{uuid.uuid4().hex}.{ext}'
    save_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, 'wb') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    url = f'{settings.MEDIA_URL}uploads/{filename}'
    return ok({'url': url, 'fileName': f.name})


# ======================== 文件分享 ========================

def _file_share_to_dict(f, include_author=True):
    d = {
        '_id': str(f.id), 'userId': f.user_id, 'title': f.title,
        'description': f.description, 'fileUrl': f.file_url, 'fileName': f.file_name,
        'status': f.status,
        'createdAt': f.created_at.isoformat() if f.created_at else '',
    }
    if include_author:
        try:
            u = User.objects.get(openid=f.user_id)
            d['authorName'] = u.nickname
            d['authorAvatarUrl'] = u.avatar_url or ''
        except User.DoesNotExist:
            d['authorName'] = '未知'
            d['authorAvatarUrl'] = ''
    return d


@csrf_exempt
@require_POST
def file_share_create(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    if not user.profile_completed:
        return err('PROFILE_INCOMPLETE', '请先完善个人资料')
    body = get_body(request)
    title = (body.get('title') or '').strip()
    file_url = body.get('fileUrl') or ''
    if not title or not file_url:
        return err('INVALID_PARAMS', '标题和文件链接为必填')
    fs = FileShare.objects.create(
        user_id=openid,
        title=title,
        description=body.get('description', ''),
        file_url=file_url,
        file_name=body.get('fileName', ''),
        status='pending',
    )
    return ok({'id': str(fs.id)})


@csrf_exempt
@require_POST
def file_share_list(request):
    openid = request.user_token
    body = get_body(request)
    page = max(int(body.get('page', 1)), 1)
    page_size = min(max(int(body.get('pageSize', 20)), 5), 50)
    my_files = body.get('myFiles')
    if my_files:
        qs = FileShare.objects.filter(user_id=openid).order_by('-created_at')
    else:
        qs = FileShare.objects.filter(status='approved').order_by('-created_at')
    total = qs.count()
    start = (page - 1) * page_size
    items = qs[start:start + page_size]
    return ok({
        'items': [_file_share_to_dict(f) for f in items],
        'total': total,
        'hasMore': start + page_size < total,
    })


# ======================== 管理员接口 ========================

def _check_admin(request):
    user = get_or_create_user(request.user_token)
    if user.role != 'admin':
        return None, err('UNAUTHORIZED', '需要管理员权限')
    return user, None


@csrf_exempt
@require_POST
def admin_reports(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    if is_super_admin_user(admin):
        base = Post.objects.exclude(category='emotion')
    else:
        base = Post.objects.filter(author__user_class=ac).exclude(category='emotion')
    flagged_qs = base.filter(status='flagged').order_by('-created_at')[:100]
    all_qs = base.order_by('-pinned', '-created_at')[:200]
    flagged_list = [post_to_dict(p, reveal_author=True) for p in flagged_qs]
    all_list = [post_to_dict(p, reveal_author=True) for p in all_qs]
    return ok({
        'flagged': flagged_list,
        'allPosts': all_list,
        'posts': all_list,
        'total': len(all_list),
        'hasMore': False,
    })


@csrf_exempt
@require_POST
def admin_post_override(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    p, e2 = _ensure_post_admin_scope(admin, body.get('postId'))
    if e2:
        return e2
    new_status = body.get('newStatus', '')
    Post.objects.filter(id=p.id).update(status=new_status)
    try:
        author = User.objects.get(openid=p.author_id)
        _log_admin_action(admin, 'post_override', 'post', p.id, {
            'newStatus': new_status,
            'summary': (p.content or '')[:120],
            'authorNickname': author.nickname,
            'authorClass': author.user_class or '',
        })
    except User.DoesNotExist:
        _log_admin_action(admin, 'post_override', 'post', p.id, {'newStatus': new_status})
    return ok()


@csrf_exempt
@require_POST
def admin_post_category(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    p, e2 = _ensure_post_admin_scope(admin, body.get('postId'))
    if e2:
        return e2
    Post.objects.filter(id=p.id).update(category=body['newCategory'])
    return ok()


@csrf_exempt
@require_POST
def admin_post_batch_override(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    ids = body.get('postIds', [])
    new_status = body.get('newStatus', '')
    ac = _admin_class_value(admin)
    id_list = [int(i) for i in ids]
    if is_super_admin_user(admin):
        allowed_ids = list(Post.objects.filter(id__in=id_list).values_list('id', flat=True))
    else:
        allowed_ids = list(
            Post.objects.filter(
                id__in=id_list,
                author__user_class=ac,
            ).values_list('id', flat=True)
        )
    if allowed_ids:
        Post.objects.filter(id__in=allowed_ids).update(status=new_status)
        for pid in allowed_ids:
            try:
                p = Post.objects.get(id=pid)
                author = User.objects.get(openid=p.author_id)
                _log_admin_action(admin, 'post_override', 'post', pid, {
                    'newStatus': new_status,
                    'batch': True,
                    'authorNickname': author.nickname,
                    'authorClass': author.user_class or '',
                })
            except (Post.DoesNotExist, User.DoesNotExist):
                pass
    return ok({'count': len(allowed_ids)})


@csrf_exempt
@require_POST
def admin_post_real_author(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    try:
        p = Post.objects.get(id=int(body['postId']))
        if not _user_in_admin_class(admin, p.author_id):
            return ok(None)
        u = User.objects.get(openid=p.author_id)
        return ok({'authorId': p.author_id, 'nickname': u.nickname, 'class': u.user_class})
    except (Post.DoesNotExist, User.DoesNotExist):
        return ok(None)


@csrf_exempt
@require_POST
def admin_post_pin(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    p, e2 = _ensure_post_admin_scope(admin, body.get('postId'))
    if e2:
        return e2
    Post.objects.filter(id=p.id).update(pinned=True)
    return ok()


@csrf_exempt
@require_POST
def admin_post_unpin(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    p, e2 = _ensure_post_admin_scope(admin, body.get('postId'))
    if e2:
        return e2
    Post.objects.filter(id=p.id).update(pinned=False)
    return ok()


@csrf_exempt
@require_POST
def admin_user_score(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    tid = body.get('userId') or body.get('targetUserId')
    if not tid:
        return err('INVALID_PARAMS', '缺少用户ID')
    if not is_super_admin_user(admin) and not _user_in_admin_class(admin, tid):
        return err('FORBIDDEN', '仅可操作本班用户')
    score_val = int(body.get('delta', body.get('score', 0)))
    score_delta = score_val * 2  # 导生评分×2
    User.objects.filter(openid=tid).update(score=F('score') + score_delta)
    PointsLog.objects.create(user_id=tid, delta=score_delta, log_type='score', reason='admin_score')
    return ok({'pointsDelta': score_delta})


@csrf_exempt
@require_POST
def admin_user_profile(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    tid = body.get('userId') or body.get('targetUserId')
    if not tid:
        return err('INVALID_PARAMS', '缺少用户ID')
    try:
        u = User.objects.get(openid=tid)
    except User.DoesNotExist:
        return err('NOT_FOUND', '用户不存在')

    post_count = Post.objects.filter(author_id=tid).exclude(category='emotion').count()
    ach_count = Achievement.objects.filter(user_id=tid).count()
    logs = PointsLog.objects.filter(user_id=tid)[:10]
    return ok({
        'user': user_to_dict(u),
        'stats': {'postCount': post_count, 'achievementCount': ach_count},
        'recentPointsLog': [{
            '_id': str(l.id), 'delta': l.delta, 'reason': l.reason,
            'createdAt': l.created_at.isoformat() if l.created_at else '',
        } for l in logs],
    })


@csrf_exempt
@require_POST
def admin_user_list(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    kw = (body.get('keyword') or '').strip()
    qs = User.objects.all().order_by('-created_at')
    if kw:
        qs = qs.filter(
            Q(nickname__icontains=kw) | Q(openid__icontains=kw)
            | Q(user_class__icontains=kw) | Q(student_id__icontains=kw)
            | Q(username__icontains=kw)
        )
    return ok({'users': [user_to_dict(u) for u in qs[:200]]})


@csrf_exempt
@require_POST
def admin_user_posts(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    tid = body.get('targetUserId')
    if not tid:
        return err('INVALID_PARAMS', '缺少用户ID')
    if not User.objects.filter(openid=tid).exists():
        return err('NOT_FOUND', '用户不存在')
    posts = Post.objects.filter(author_id=tid)
    return ok({'posts': [post_to_dict(p, reveal_author=True) for p in posts]})


@csrf_exempt
@require_POST
def admin_user_contact(request):
    admin, e = _check_admin(request)
    if e: return e
    return ok()


@csrf_exempt
@require_POST
def admin_emotion_list(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    if is_super_admin_user(admin):
        posts = Post.objects.filter(category='emotion').order_by('-created_at')[:100]
    else:
        posts = Post.objects.filter(
            category='emotion', author__user_class=ac,
        ).order_by('-created_at')[:100]
    return ok({'posts': [post_to_dict(p, reveal_author=True) for p in posts]})


@csrf_exempt
@require_POST
def admin_emotion_history(request):
    """本导生已回复过的同班情感倾诉"""
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    commented_by_me = Comment.objects.filter(
        post_id=OuterRef('pk'),
        author_id=admin.openid,
        is_admin=True,
    )
    emo = Post.objects.filter(category='emotion')
    if not is_super_admin_user(admin):
        emo = emo.filter(author__user_class=ac)
    posts = emo.annotate(
        _has_my_reply=Exists(commented_by_me),
    ).filter(_has_my_reply=True).order_by('-created_at')[:100]
    return ok({'posts': [post_to_dict(p, reveal_author=True) for p in posts]})


@csrf_exempt
@require_POST
def admin_review_history(request):
    """本导生对本班的处理记录；最高管理员亦仅展示其资料中分管班级相关记录"""
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    if not is_allowed_class(ac):
        return ok({'logs': []})
    logs = AdminActionLog.objects.filter(
        admin_id=admin.openid,
        detail__authorClass=ac,
    ).order_by('-created_at')[:200]
    return ok({'logs': [{
        '_id': str(l.id),
        'action': l.action,
        'targetType': l.target_type,
        'targetId': l.target_id,
        'detail': l.detail,
        'createdAt': l.created_at.isoformat() if l.created_at else '',
    } for l in logs]})


@csrf_exempt
@require_POST
def admin_invite_generate(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    code = 'INV' + uuid.uuid4().hex[:6].upper()
    Invite.objects.create(code=code, role=body.get('role', 'admin'))
    return ok({'inviteCode': code})


@csrf_exempt
@require_POST
def admin_super_promote_user(request):
    """仅最高管理员可将任意用户设为导生（不消耗邀请码）"""
    admin, e = _check_admin(request)
    if e:
        return e
    if not is_super_admin_user(admin):
        return err('FORBIDDEN', '仅最高管理员可指定导生')
    body = get_body(request)
    tid = body.get('targetUserId') or body.get('userId')
    if not tid:
        return err('INVALID_PARAMS', '缺少用户ID')
    try:
        u = User.objects.get(openid=tid)
    except User.DoesNotExist:
        return err('NOT_FOUND', '用户不存在')
    if u.role == 'admin':
        return ok({'alreadyAdmin': True, 'user': user_to_dict(u, post_count_exclude_emotion=True)})
    u.role = 'admin'
    u.save(update_fields=['role', 'updated_at'])
    return ok({'user': user_to_dict(u, post_count_exclude_emotion=True)})


@csrf_exempt
@require_POST
def admin_comment_add(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    p, e2 = _ensure_post_admin_scope(admin, body.get('postId'))
    if e2:
        return e2
    content = (body.get('content') or '').strip()
    if not content:
        return err('INVALID_PARAMS', '评论不能为空')
    if len(content) > 500:
        return err('INVALID_PARAMS', '评论过长')
    if not sensitive_check.content_passes(content):
        return err('SENSITIVE_CONTENT', '评论包含敏感词，无法发送')
    parent = None
    raw_parent = body.get('parentCommentId') or body.get('replyToCommentId')
    if raw_parent:
        try:
            pid = int(raw_parent)
            parent = Comment.objects.get(id=pid, post_id=p.id)
        except (ValueError, TypeError, Comment.DoesNotExist):
            return err('INVALID_PARAMS', '回复的评论不存在')
    c = Comment.objects.create(
        post_id=p.id,
        parent_comment=parent,
        author_id=admin.openid,
        author_name=admin.nickname,
        is_admin=True,
        content=content,
    )
    return ok({'commentId': str(c.id)})


@csrf_exempt
@require_POST
def admin_achievement_pending(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    if is_super_admin_user(admin):
        achs = Achievement.objects.filter(status='pending')
    else:
        achs = Achievement.objects.filter(status='pending', user__user_class=ac)
    return ok({'achievements': [ach_to_dict(a) for a in achs]})


@csrf_exempt
@require_POST
def admin_achievement_approve(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    ach_id = body.get('achievementId') or body.get('id')
    if not ach_id:
        return err('INVALID_PARAMS', '缺少成果ID')
    try:
        a = Achievement.objects.get(id=int(ach_id), status='pending')
    except Achievement.DoesNotExist:
        return err('NOT_FOUND', '成果不存在或已处理')
    if not _user_in_admin_class(admin, a.user_id):
        return err('FORBIDDEN', '无权审核其他班级的成果')

    level = min(max(a.level, 1), 5)
    exp_gain = min(ACHIEVEMENT_BASE_EXP + (level - 1) * ACHIEVEMENT_LEVEL_MULTIPLIER, ACHIEVEMENT_MAX_EXP)
    a.status = 'approved'
    a.exp_awarded = exp_gain
    a.save()

    cat_field = a.category
    user = get_or_create_user(a.user_id)
    counts = user.achievement_counts or {}
    counts[cat_field] = counts.get(cat_field, 0) + 1
    score_gain = exp_gain // EXP_TO_SCORE_RATIO
    User.objects.filter(openid=a.user_id).update(
        exp=F('exp') + exp_gain, score=F('score') + score_gain,
        achievement_counts=counts,
    )
    PointsLog.objects.create(
        user_id=a.user_id, delta=exp_gain, log_type='exp',
        reason='achievement_approved', related_id=str(a.id),
    )
    try:
        author = User.objects.get(openid=a.user_id)
        _log_admin_action(admin, 'achievement_approve', 'achievement', a.id, {
            'title': a.title,
            'authorNickname': author.nickname,
            'authorClass': author.user_class or '',
            'expGain': exp_gain,
        })
    except User.DoesNotExist:
        _log_admin_action(admin, 'achievement_approve', 'achievement', a.id, {'title': a.title})
    return ok({'expGain': exp_gain})


@csrf_exempt
@require_POST
def admin_achievement_reject(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    ach_id = body.get('achievementId') or body.get('id')
    if not ach_id:
        return err('INVALID_PARAMS', '缺少成果ID')
    try:
        a = Achievement.objects.get(id=int(ach_id), status='pending')
    except Achievement.DoesNotExist:
        return err('NOT_FOUND', '成果不存在或已处理')
    if not _user_in_admin_class(admin, a.user_id):
        return err('FORBIDDEN', '无权审核其他班级的成果')
    Achievement.objects.filter(id=a.id).update(status='rejected')
    try:
        author = User.objects.get(openid=a.user_id)
        _log_admin_action(admin, 'achievement_reject', 'achievement', a.id, {
            'title': a.title,
            'reason': (body.get('reason') or '')[:200],
            'authorNickname': author.nickname,
            'authorClass': author.user_class or '',
        })
    except User.DoesNotExist:
        _log_admin_action(admin, 'achievement_reject', 'achievement', a.id, {'title': a.title})
    return ok()


@csrf_exempt
@require_POST
def admin_growth_book(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    tid = body['targetUserId']
    if not _user_in_admin_class(admin, tid):
        return err('FORBIDDEN', '无权查看其他班级用户')
    achs = Achievement.objects.filter(user_id=tid, status='approved')
    try:
        u = User.objects.get(openid=tid)
        user_data = {'nickname': u.nickname, 'class': u.user_class, 'exp': u.exp, 'achievementCounts': u.achievement_counts}
    except User.DoesNotExist:
        user_data = None
    return ok({'achievements': [ach_to_dict(a) for a in achs], 'user': user_data})


def _file_share_user_ids_in_class(admin_class):
    return User.objects.filter(user_class=admin_class).values_list('openid', flat=True)


@csrf_exempt
@require_POST
def admin_file_share_pending(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    if is_super_admin_user(admin):
        items = FileShare.objects.filter(status='pending').order_by('-created_at')[:50]
    else:
        uids = _file_share_user_ids_in_class(ac)
        items = FileShare.objects.filter(status='pending', user_id__in=uids).order_by('-created_at')[:50]
    return ok({'items': [_file_share_to_dict(f) for f in items]})


@csrf_exempt
@require_POST
def admin_file_share_approve(request):
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    fid = body.get('fileShareId')
    if not fid:
        return err('INVALID_PARAMS', '缺少文件ID')
    try:
        fs = FileShare.objects.get(id=int(fid), status='pending')
    except FileShare.DoesNotExist:
        return err('NOT_FOUND', '文件不存在或已审核')
    if not _user_in_admin_class(admin, fs.user_id):
        return err('FORBIDDEN', '无权审核其他班级的文件')
    FileShare.objects.filter(id=fs.id).update(status='approved')
    try:
        author = User.objects.get(openid=fs.user_id)
        _log_admin_action(admin, 'file_approve', 'file_share', fs.id, {
            'title': fs.title,
            'authorNickname': author.nickname,
            'authorClass': author.user_class or '',
        })
    except User.DoesNotExist:
        _log_admin_action(admin, 'file_approve', 'file_share', fs.id, {'title': fs.title})
    return ok()


@csrf_exempt
@require_POST
def admin_file_share_list(request):
    """导生获取文件列表：支持 status 筛选 pending / approved"""
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    ac = _admin_class_value(admin)
    body = get_body(request)
    status = body.get('status', '')
    if is_super_admin_user(admin):
        qs = FileShare.objects.all().order_by('-created_at')
    else:
        uids = _file_share_user_ids_in_class(ac)
        qs = FileShare.objects.filter(user_id__in=uids).order_by('-created_at')
    if status == 'pending':
        qs = qs.filter(status='pending')
    elif status == 'approved':
        qs = qs.filter(status='approved')
    items = list(qs[:100])
    return ok({'items': [_file_share_to_dict(f) for f in items]})


@csrf_exempt
@require_POST
def admin_file_share_delete(request):
    """导生删除已发布的文件"""
    admin, e = _check_admin(request)
    if e: return e
    e2 = _admin_class_err(admin)
    if e2:
        return e2
    body = get_body(request)
    fid = body.get('fileShareId')
    if not fid:
        return err('INVALID_PARAMS', '缺少文件ID')
    try:
        fs = FileShare.objects.get(id=int(fid))
    except FileShare.DoesNotExist:
        return err('NOT_FOUND', '文件不存在')
    if not _user_in_admin_class(admin, fs.user_id):
        return err('FORBIDDEN', '无权删除其他班级的文件')
    deleted, _ = FileShare.objects.filter(id=fs.id).delete()
    try:
        author = User.objects.get(openid=fs.user_id)
        _log_admin_action(admin, 'file_delete', 'file_share', fid, {
            'title': fs.title,
            'authorNickname': author.nickname,
            'authorClass': author.user_class or '',
        })
    except User.DoesNotExist:
        _log_admin_action(admin, 'file_delete', 'file_share', fid, {'title': fs.title})
    return ok({'deleted': deleted})


@csrf_exempt
@require_POST
def shop_items(request):
    openid = request.user_token
    items = ShopItem.objects.filter(stock__gt=0).order_by('sort_order', 'price')
    return ok({'items': [{
        '_id': str(i.id), 'itemKey': i.item_key, 'title': i.title,
        'imageUrl': i.image_url, 'price': i.price, 'stock': i.stock,
    } for i in items]})


@csrf_exempt
@require_POST
def shop_exchange(request):
    openid = request.user_token
    body = get_body(request)
    item_key = body.get('itemKey') or ''
    if not item_key:
        return err('INVALID_PARAMS', '请选择兑换商品')
    try:
        user = User.objects.get(openid=openid)
    except User.DoesNotExist:
        return err('UNAUTHORIZED', '请先登录')
    try:
        item = ShopItem.objects.get(item_key=item_key, stock__gt=0)
    except ShopItem.DoesNotExist:
        return err('NOT_FOUND', '商品不存在或已售罄')
    if user.score < item.price:
        return err('INSUFFICIENT_SCORE', '积分不足')
    user.score -= item.price
    user.save(update_fields=['score'])
    item.stock -= 1
    item.save(update_fields=['stock'])
    ExchangeRecord.objects.create(
        user_id=openid, item_key=item_key, item_title=item.title, price=item.price
    )
    return ok({'score': user.score})


@csrf_exempt
@require_POST
def shop_my_exchanges(request):
    openid = request.user_token
    records = ExchangeRecord.objects.filter(user_id=openid).order_by('-created_at')[:50]
    return ok({'records': [{
        '_id': str(r.id), 'itemKey': r.item_key, 'itemTitle': r.item_title,
        'price': r.price, 'createdAt': r.created_at.isoformat() if r.created_at else '',
    } for r in records]})


@csrf_exempt
@require_POST
def admin_shop_items(request):
    admin, e = _check_admin(request)
    if e: return e
    items = ShopItem.objects.all().order_by('sort_order', 'price')
    return ok({'items': [{
        '_id': str(i.id), 'itemKey': i.item_key, 'title': i.title,
        'imageUrl': i.image_url, 'price': i.price, 'stock': i.stock,
    } for i in items]})


@csrf_exempt
@require_POST
def admin_shop_update_stock(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    item_key = body.get('itemKey') or ''
    stock = int(body.get('stock', 0))
    if not item_key:
        return err('INVALID_PARAMS', '缺少商品标识')
    ShopItem.objects.filter(item_key=item_key).update(stock=max(0, stock))
    return ok()


@csrf_exempt
@require_POST
def admin_export_data(request):
    admin, e = _check_admin(request)
    if e: return e

    data = {
        'exported_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'users': [user_to_dict(u) for u in User.objects.all()],
        'posts': [post_to_dict(p, reveal_author=True) for p in Post.objects.all()],
        'comments': [
            {'_id': str(c.id), 'postId': str(c.post_id), 'authorId': c.author_id,
             'authorName': c.author_name, 'isAdmin': c.is_admin,
             'content': c.content, 'createdAt': c.created_at.isoformat()}
            for c in Comment.objects.all()
        ],
        'achievements': [ach_to_dict(a) for a in Achievement.objects.all()],
        'invites': [
            {'code': i.code, 'role': i.role, 'usedBy': i.used_by or '',
             'createdAt': i.created_at.isoformat()}
            for i in Invite.objects.all()
        ],
        'points_log': [
            {'userId': l.user_id, 'delta': l.delta, 'reason': l.reason,
             'relatedId': l.related_id, 'createdAt': l.created_at.isoformat()}
            for l in PointsLog.objects.all().order_by('-created_at')[:500]
        ],
        'messages': [
            {'fromId': m.from_id, 'fromName': m.from_name, 'toId': m.to_id,
             'content': m.content, 'read': m.read, 'createdAt': m.created_at.isoformat()}
            for m in Message.objects.all().order_by('-created_at')[:1000]
        ],
    }
    return ok(data)

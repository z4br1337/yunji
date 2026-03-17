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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import models as db_models
from django.db.models import Q, F, Count, Max
from django.conf import settings

from .models import User, Post, Comment, Achievement, Invite, PointsLog, Message

EXP_PER_POST = 10
ACHIEVEMENT_BASE_EXP = 500
ACHIEVEMENT_LEVEL_MULTIPLIER = 500
ACHIEVEMENT_MAX_EXP = 2500
PAGE_SIZE = 20


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
        defaults={'exp': 10, 'score': 10, 'achievement_counts': {}}
    )
    return user


def require_admin(user):
    return user.role == 'admin'


def user_to_dict(u):
    return {
        '_id': u.openid,
        'username': u.username or '',
        'nickname': u.nickname, 'class': u.user_class,
        'avatarUrl': u.avatar_url,
        'profileCompleted': u.profile_completed,
        'role': u.role, 'exp': u.exp, 'score': u.score,
        'postCount': u.post_count,
        'achievementCounts': u.achievement_counts or {},
        'growthBookPublic': u.growth_book_public,
        'inviteUsed': u.invite_used,
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
    if reveal_author:
        try:
            author = User.objects.get(openid=p.author_id)
            d['authorName'] = author.nickname
            d['authorClass'] = author.user_class
        except User.DoesNotExist:
            d['authorName'] = '未知'
            d['authorClass'] = ''
    return d


def ach_to_dict(a):
    return {
        '_id': str(a.id), 'userId': a.user_id,
        'title': a.title, 'description': a.description,
        'category': a.category, 'dimension': a.dimension,
        'subcategory': a.subcategory, 'level': a.level,
        'points': a.points, 'expAwarded': a.exp_awarded,
        'images': a.images or [], 'status': a.status,
        'createdAt': a.created_at.isoformat() if a.created_at else '',
    }


# ======================== 密码工具 ========================

def _hash_password(password):
    salt = os.environ.get('PASSWORD_SALT', 'yunji_salt_2026')
    return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()


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
        exp=10, score=10, achievement_counts={},
    )
    return ok({
        'user': user_to_dict(user),
        'token': openid,
    })


@csrf_exempt
@require_POST
def user_login(request):
    body = get_body(request)
    username = (body.get('username') or '').strip()
    password = (body.get('password') or '').strip()

    if username and password:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return err('USER_NOT_FOUND', '账号不存在')
        if user.password_hash != _hash_password(password):
            return err('WRONG_PASSWORD', '密码错误')
        return ok({
            'user': user_to_dict(user),
            'token': user.openid,
            'profileCompleted': user.profile_completed,
        })

    token = request.user_token
    if not token:
        return err('UNAUTHORIZED', '请先登录')
    user = get_or_create_user(token)
    return ok({
        'user': user_to_dict(user),
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

    if nickname is not None:
        user.nickname = nickname
    if user_class is not None:
        user.user_class = user_class
    if growth_book_public is not None:
        user.growth_book_public = bool(growth_book_public)

    if nickname and user_class:
        user.profile_completed = True

    user.save()
    return ok({'user': user_to_dict(user), 'profileCompleted': user.profile_completed})


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
    is_flagged = bool(body.get('flagged'))

    p = Post.objects.create(
        author_id=openid,
        is_anonymous=bool(body.get('isAnonymous')),
        visible_author_name='匿名用户' if body.get('isAnonymous') else user.nickname,
        content=body.get('content', ''),
        images=body.get('images', []),
        category=body.get('category', 'cognition'),
        status='flagged' if is_flagged else 'published',
        notify_admin=bool(body.get('notifyAdminFlag')),
        need_offline=bool(body.get('needOffline')),
        offline_time=body.get('offlineTime', ''),
        offline_place=body.get('offlinePlace', ''),
        flagged=is_flagged,
        flagged_words=body.get('flaggedWords', []),
        flagged_categories=body.get('flaggedCategories', []),
        flagged_highlighted=body.get('flaggedHighlighted', ''),
    )

    exp_gain = 0
    if not is_flagged:
        exp_gain = EXP_PER_POST
        User.objects.filter(openid=openid).update(
            exp=F('exp') + exp_gain,
            score=F('score') + exp_gain,
            post_count=F('post_count') + 1,
        )
        PointsLog.objects.create(
            user_id=openid, delta=exp_gain, log_type='exp',
            reason='post_published', related_id=str(p.id),
        )

    return ok({'postId': str(p.id), 'expGain': exp_gain})


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
    return ok({'posts': [post_to_dict(p, reveal_author=user.role == 'admin')], 'total': 1, 'hasMore': False})


# ======================== 评论 ========================

@csrf_exempt
@require_POST
def comment_add(request):
    openid = request.user_token
    user = get_or_create_user(openid)
    body = get_body(request)
    c = Comment.objects.create(
        post_id=int(body.get('postId')),
        author_id=openid,
        author_name=user.nickname,
        is_admin=user.role == 'admin',
        content=body.get('content', ''),
    )
    return ok({'commentId': str(c.id)})


@csrf_exempt
@require_POST
def comment_list(request):
    body = get_body(request)
    post_id = body.get('postId')
    comments = Comment.objects.filter(post_id=int(post_id))
    return ok({'comments': [{
        '_id': str(c.id), 'postId': str(c.post_id), 'authorId': c.author_id,
        'authorName': c.author_name, 'isAdmin': c.is_admin, 'content': c.content,
        'createdAt': c.created_at.isoformat() if c.created_at else '',
    } for c in comments]})


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
    is_admin = viewer.role == 'admin'

    try:
        target = User.objects.get(openid=target_id)
    except User.DoesNotExist:
        return err('NOT_FOUND', '用户不存在')

    if not is_owner and not is_admin and not target.growth_book_public:
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
    body = get_body(request)
    f = body.get('filter', {})
    page = int(body.get('page', 1))
    qs = Post.objects.all()
    if f.get('status'):
        qs = qs.filter(status=f['status'])
    total = qs.count()
    start = (page - 1) * PAGE_SIZE
    return ok({
        'posts': [post_to_dict(p, reveal_author=True) for p in qs[start:start + PAGE_SIZE]],
        'total': total, 'hasMore': start + PAGE_SIZE < total,
    })


@csrf_exempt
@require_POST
def admin_post_override(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    Post.objects.filter(id=int(body['postId'])).update(status=body['newStatus'])
    return ok()


@csrf_exempt
@require_POST
def admin_post_category(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    Post.objects.filter(id=int(body['postId'])).update(category=body['newCategory'])
    return ok()


@csrf_exempt
@require_POST
def admin_post_batch_override(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    ids = body.get('postIds', [])
    Post.objects.filter(id__in=[int(i) for i in ids]).update(status=body['newStatus'])
    return ok({'count': len(ids)})


@csrf_exempt
@require_POST
def admin_post_real_author(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    try:
        p = Post.objects.get(id=int(body['postId']))
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
    Post.objects.filter(id=int(body['postId'])).update(pinned=True)
    return ok()


@csrf_exempt
@require_POST
def admin_post_unpin(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    Post.objects.filter(id=int(body['postId'])).update(pinned=False)
    return ok()


@csrf_exempt
@require_POST
def admin_user_score(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    delta = int(body.get('score', 0)) * 2
    User.objects.filter(openid=body['targetUserId']).update(exp=F('exp') + delta, score=F('score') + delta)
    PointsLog.objects.create(user_id=body['targetUserId'], delta=delta, log_type='exp', reason='admin_score')
    return ok({'pointsDelta': delta})


@csrf_exempt
@require_POST
def admin_user_profile(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    tid = body['targetUserId']
    try:
        u = User.objects.get(openid=tid)
    except User.DoesNotExist:
        return err('NOT_FOUND', '用户不存在')

    post_count = Post.objects.filter(author_id=tid).count()
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
    body = get_body(request)
    kw = body.get('keyword', '')
    qs = User.objects.all()
    if kw:
        qs = qs.filter(Q(nickname__icontains=kw) | Q(user_class__icontains=kw) | Q(openid__icontains=kw))
    return ok({'users': [user_to_dict(u) for u in qs[:50]]})


@csrf_exempt
@require_POST
def admin_user_posts(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    posts = Post.objects.filter(author_id=body['targetUserId'])
    return ok({'posts': [post_to_dict(p, reveal_author=True) for p in posts]})


@csrf_exempt
@require_POST
def admin_user_contact(request):
    admin, e = _check_admin(request)
    if e: return e
    return ok()


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
def admin_comment_add(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    c = Comment.objects.create(
        post_id=int(body['postId']),
        author_id=admin.openid,
        author_name=admin.nickname,
        is_admin=True,
        content=body.get('content', ''),
    )
    return ok({'commentId': str(c.id)})


@csrf_exempt
@require_POST
def admin_achievement_pending(request):
    admin, e = _check_admin(request)
    if e: return e
    achs = Achievement.objects.filter(status='pending')
    return ok({'achievements': [ach_to_dict(a) for a in achs]})


@csrf_exempt
@require_POST
def admin_achievement_approve(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    try:
        a = Achievement.objects.get(id=int(body['achievementId']), status='pending')
    except Achievement.DoesNotExist:
        return err('NOT_FOUND', '成果不存在或已处理')

    level = min(max(a.level, 1), 5)
    exp_gain = min(ACHIEVEMENT_BASE_EXP + (level - 1) * ACHIEVEMENT_LEVEL_MULTIPLIER, ACHIEVEMENT_MAX_EXP)
    a.status = 'approved'
    a.exp_awarded = exp_gain
    a.save()

    cat_field = a.category
    user = get_or_create_user(a.user_id)
    counts = user.achievement_counts or {}
    counts[cat_field] = counts.get(cat_field, 0) + 1
    User.objects.filter(openid=a.user_id).update(
        exp=F('exp') + exp_gain, score=F('score') + exp_gain,
        achievement_counts=counts,
    )
    PointsLog.objects.create(
        user_id=a.user_id, delta=exp_gain, log_type='exp',
        reason='achievement_approved', related_id=str(a.id),
    )
    return ok({'expGain': exp_gain})


@csrf_exempt
@require_POST
def admin_achievement_reject(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    Achievement.objects.filter(id=int(body['achievementId'])).update(status='rejected')
    return ok()


@csrf_exempt
@require_POST
def admin_growth_book(request):
    admin, e = _check_admin(request)
    if e: return e
    body = get_body(request)
    tid = body['targetUserId']
    achs = Achievement.objects.filter(user_id=tid, status='approved')
    try:
        u = User.objects.get(openid=tid)
        user_data = {'nickname': u.nickname, 'class': u.user_class, 'exp': u.exp, 'achievementCounts': u.achievement_counts}
    except User.DoesNotExist:
        user_data = None
    return ok({'achievements': [ach_to_dict(a) for a in achs], 'user': user_data})


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

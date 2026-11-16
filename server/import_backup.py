#!/usr/bin/env python3
"""
Import backup JSON into local SQLite database.
Run from server/ directory:
  python manage.py migrate --noinput
  python import_backup.py [backup_json_path]

Default backup file: D:/YUNJI BACKUP/latest.json
All user passwords reset to 123456 (export does not include password hashes).
"""
import os
import sys
import json
import urllib.request
from datetime import datetime

# 确保控制台输出 UTF-8，避免中文乱码
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yunji_server.settings')
os.environ.setdefault('DATA_DIR', BASE_DIR)

import django
django.setup()

from django.utils import timezone
from django.db import transaction
from api.models import (
    User, Post, Comment, Achievement, PointsLog, Message,
)
from api.views import _hash_password

DEFAULT_PASSWORD = '123456'


def parse_dt(s):
    if not s:
        return None
    s = s.strip()
    try:
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.get_current_timezone())
        return dt
    except Exception:
        return None


def load_json(path):
    """读取备份 JSON；支持本地文件或 http(s) URL。"""
    if path.startswith('http://') or path.startswith('https://'):
        with urllib.request.urlopen(path, timeout=180) as resp:
            return json.loads(resp.read().decode('utf-8'))
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_media_paths(obj, found):
    if isinstance(obj, str):
        if '/media/' in obj:
            idx = obj.find('/media/')
            rel = obj[idx:].split('?')[0].split('#')[0]
            if rel:
                found.add(rel)
    elif isinstance(obj, (list, tuple)):
        for x in obj:
            collect_media_paths(x, found)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_media_paths(v, found)


def download_missing_media(data, media_base):
    """把 JSON 中引用的 /media/... 文件从 media_base 下载到本地 MEDIA_ROOT。"""
    from django.conf import settings
    media_root = str(settings.MEDIA_ROOT)
    found = set()
    collect_media_paths(data, found)
    print('Media refs: %d (base=%s)' % (len(found), media_base))
    ok = skip = fail = 0
    for rel in sorted(found):
        local_rel = rel[len('/media/'):]
        local_path = os.path.join(media_root, local_rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        if os.path.isfile(local_path):
            skip += 1
            continue
        url = media_base.rstrip('/') + rel
        try:
            urllib.request.urlretrieve(url, local_path)
            ok += 1
        except Exception as e:
            fail += 1
            print('  fail', url, e)
            if os.path.isfile(local_path):
                try:
                    os.remove(local_path)
                except OSError:
                    pass
    print('Media done: downloaded %d, existed %d, failed %d' % (ok, skip, fail))


def wipe():
    print('Clearing local tables...')
    PointsLog.objects.all().delete()
    Message.objects.all().delete()
    Comment.objects.all().delete()
    Post.objects.all().delete()
    Achievement.objects.all().delete()
    User.objects.all().delete()


def import_users(users):
    print('Importing users: %d' % len(users))
    for u in users:
        openid = u['_id']
        email = (u.get('email') or '').strip() or None
        username = (u.get('username') or '').strip() or None
        student_id = (u.get('studentId') or '').strip() or None
        invite_used = (u.get('inviteUsed') or '').strip() or None
        muted = parse_dt(u.get('mutedUntil'))
        banned = parse_dt(u.get('bannedUntil'))
        created = parse_dt(u.get('createdAt'))
        updated = parse_dt(u.get('updatedAt'))
        User.objects.create(
            openid=openid,
            username=username,
            password_hash=_hash_password(DEFAULT_PASSWORD),
            nickname=u.get('nickname') or '',
            user_class=u.get('class') or '',
            avatar_url=u.get('avatarUrl') or '',
            profile_completed=bool(u.get('profileCompleted')),
            role=u.get('role') or 'user',
            exp=int(u.get('exp') or 10),
            score=int(u.get('score') or 10),
            post_count=int(u.get('postCount') or 0),
            achievement_counts=u.get('achievementCounts') or {},
            growth_book_public=bool(u.get('growthBookPublic')),
            invite_used=invite_used,
            email=email,
            student_id=student_id,
            muted_until=muted,
            banned_until=banned,
            account_deleted=bool(u.get('accountDeleted')),
        )
        updates = {}
        if created:
            updates['created_at'] = created
        if updated:
            updates['updated_at'] = updated
        if updates:
            User.objects.filter(openid=openid).update(**updates)
    from api.constants import SUPER_ADMIN_USERNAME
    User.objects.filter(username=SUPER_ADMIN_USERNAME).update(role='admin')


def import_posts(posts):
    print('Importing posts: %d' % len(posts))
    for p in posts:
        pid = int(p['_id'])
        author_id = p.get('authorId') or ''
        if not User.objects.filter(openid=author_id).exists():
            print('  skip post %d (author missing %s)' % (pid, author_id))
            continue
        created = parse_dt(p.get('createdAt'))
        updated = parse_dt(p.get('updatedAt'))
        Post.objects.create(
            id=pid,
            author_id=author_id,
            is_anonymous=bool(p.get('isAnonymous')),
            visible_author_name=p.get('visibleAuthorName') or '',
            content=p.get('content') or '',
            images=p.get('images') or [],
            category=p.get('category') or 'cognition',
            status=p.get('status') or 'published',
            pinned=bool(p.get('pinned')),
            featured=bool(p.get('featured')),
            like_count=int(p.get('likeCount') or 0),
            points_awarded=int(p.get('pointsAwarded') or 0),
            notify_admin=bool(p.get('notifyAdmin')),
            need_offline=bool(p.get('needOffline')),
            offline_time=p.get('offlineTime') or '',
            offline_place=p.get('offlinePlace') or '',
            flagged=bool(p.get('flagged')),
            flagged_words=p.get('flaggedWords') or [],
            flagged_categories=p.get('flaggedCategories') or [],
            flagged_highlighted=p.get('flaggedHighlighted') or '',
            topics=p.get('topics') or [],
        )
        updates = {}
        if created:
            updates['created_at'] = created
        if updated:
            updates['updated_at'] = updated
        if updates:
            Post.objects.filter(id=pid).update(**updates)


def import_comments(comments):
    print('Importing comments: %d' % len(comments))
    for c in comments:
        cid = int(c['_id'])
        post_id = int(c['postId'])
        if not Post.objects.filter(id=post_id).exists():
            continue
        created = parse_dt(c.get('createdAt'))
        Comment.objects.create(
            id=cid,
            post_id=post_id,
            parent_comment_id=None,
            author_id=c.get('authorId') or '',
            author_name=c.get('authorName') or '',
            is_admin=bool(c.get('isAdmin')),
            content=c.get('content') or '',
        )
        if created:
            Comment.objects.filter(id=cid).update(created_at=created)


def import_achievements(achs):
    print('Importing achievements: %d' % len(achs))
    for a in achs:
        aid = int(a['_id'])
        user_id = a.get('userId') or ''
        if not User.objects.filter(openid=user_id).exists():
            continue
        created = parse_dt(a.get('createdAt'))
        updated = parse_dt(a.get('updatedAt'))
        Achievement.objects.create(
            id=aid,
            user_id=user_id,
            title=a.get('title') or '',
            description=a.get('description') or '',
            category=a.get('category') or '',
            dimension=a.get('dimension') or '',
            subcategory=a.get('subcategory') or '',
            level=int(a.get('level') or 1),
            points=int(a.get('points') or 0),
            exp_awarded=int(a.get('expAwarded') or 0),
            images=a.get('images') or [],
            status=a.get('status') or 'pending',
        )
        updates = {}
        if created:
            updates['created_at'] = created
        if updated:
            updates['updated_at'] = updated
        if updates:
            Achievement.objects.filter(id=aid).update(**updates)


def import_points_log(logs):
    print('Importing points_log: %d' % len(logs))
    for l in logs:
        created = parse_dt(l.get('createdAt'))
        pl = PointsLog.objects.create(
            user_id=l.get('userId') or '',
            delta=int(l.get('delta') or 0),
            log_type='exp',
            reason=l.get('reason') or '',
            related_id=l.get('relatedId') or '',
        )
        if created:
            PointsLog.objects.filter(id=pl.id).update(created_at=created)


def import_messages(msgs):
    print('Importing messages: %d' % len(msgs))
    for m in msgs:
        created = parse_dt(m.get('createdAt'))
        msg = Message.objects.create(
            from_id=m.get('fromId') or '',
            from_name=m.get('fromName') or '',
            to_id=m.get('toId') or '',
            content=m.get('content') or '',
            read=bool(m.get('read')),
        )
        if created:
            Message.objects.filter(id=msg.id).update(created_at=created)


def main():
    args = sys.argv[1:]
    media_base = None
    positional = []
    for a in args:
        if a == '--media-base':
            media_base = True  # marker; next value consumed below
            continue
        if media_base is True:
            media_base = a
            continue
        positional.append(a)

    if positional:
        path = positional[0]
    else:
        path = os.environ.get('BACKUP_JSON', '/data/latest.json')

    print('Reading backup: %s' % path)
    if not path.startswith('http://') and not path.startswith('https://') and not os.path.isfile(path):
        print('Backup file not found: %s' % path)
        sys.exit(1)
    data = load_json(path)

    with transaction.atomic():
        wipe()
        import_users(data.get('users') or [])
        import_posts(data.get('posts') or [])
        import_comments(data.get('comments') or [])
        import_achievements(data.get('achievements') or [])
        import_points_log(data.get('points_log') or [])
        import_messages(data.get('messages') or [])

    if media_base:
        download_missing_media(data, media_base)

    print('')
    print('Import done.')
    print('  users: %d' % User.objects.count())
    print('  posts: %d' % Post.objects.count())
    print('  comments: %d' % Comment.objects.count())
    print('  achievements: %d' % Achievement.objects.count())
    print('  points_log: %d' % PointsLog.objects.count())
    print('  messages: %d' % Message.objects.count())
    print('')
    print('Note: all user passwords reset to %s; media files are under DATA_DIR/media/.' % DEFAULT_PASSWORD)


if __name__ == '__main__':
    main()

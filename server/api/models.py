from django.db import models
import uuid


def gen_id():
    return uuid.uuid4().hex[:16]


class User(models.Model):
    openid = models.CharField(max_length=128, unique=True, db_index=True)
    username = models.CharField(max_length=64, unique=True, null=True, blank=True, db_index=True)
    password_hash = models.CharField(max_length=256, default='')
    nickname = models.CharField(max_length=64, default='')
    user_class = models.CharField(max_length=64, default='', db_column='class_name')
    avatar_url = models.CharField(max_length=512, default='')
    profile_completed = models.BooleanField(default=False)
    role = models.CharField(max_length=16, default='user')  # user / admin
    exp = models.IntegerField(default=10)
    score = models.IntegerField(default=10)
    post_count = models.IntegerField(default=0)
    achievement_counts = models.JSONField(default=dict)
    growth_book_public = models.BooleanField(default=False)
    invite_used = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', to_field='openid')
    is_anonymous = models.BooleanField(default=False)
    visible_author_name = models.CharField(max_length=64, default='')
    content = models.TextField(default='')
    images = models.JSONField(default=list)
    category = models.CharField(max_length=32, default='cognition')
    status = models.CharField(max_length=16, default='published')
    pinned = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    notify_admin = models.BooleanField(default=False)
    need_offline = models.BooleanField(default=False)
    offline_time = models.CharField(max_length=64, default='')
    offline_place = models.CharField(max_length=128, default='')
    flagged = models.BooleanField(default=False)
    flagged_words = models.JSONField(default=list)
    flagged_categories = models.JSONField(default=list)
    flagged_highlighted = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-pinned', '-created_at']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_id = models.CharField(max_length=128)
    author_name = models.CharField(max_length=64, default='')
    is_admin = models.BooleanField(default=False)
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']


class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', to_field='openid')
    title = models.CharField(max_length=128)
    description = models.TextField(default='')
    category = models.CharField(max_length=32)
    dimension = models.CharField(max_length=32, default='')
    subcategory = models.CharField(max_length=32, default='')
    level = models.IntegerField(default=1)
    points = models.IntegerField(default=0)
    exp_awarded = models.IntegerField(default=0)
    images = models.JSONField(default=list)
    status = models.CharField(max_length=16, default='pending')  # pending / approved / rejected
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'achievements'
        ordering = ['-created_at']


class Invite(models.Model):
    code = models.CharField(max_length=32, unique=True)
    role = models.CharField(max_length=16, default='admin')
    used_by = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invites'


class PointsLog(models.Model):
    user_id = models.CharField(max_length=128, db_index=True)
    delta = models.IntegerField(default=0)
    log_type = models.CharField(max_length=16, default='exp', db_column='type')
    reason = models.CharField(max_length=64)
    related_id = models.CharField(max_length=64, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'points_log'
        ordering = ['-created_at']


class Message(models.Model):
    from_id = models.CharField(max_length=128, db_index=True)
    from_name = models.CharField(max_length=64, default='')
    to_id = models.CharField(max_length=128, db_index=True)
    content = models.TextField(default='')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']


class FileShare(models.Model):
    user_id = models.CharField(max_length=128, db_index=True)
    title = models.CharField(max_length=128)
    description = models.TextField(default='')
    file_url = models.CharField(max_length=512)
    file_name = models.CharField(max_length=256, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'file_shares'
        ordering = ['-created_at']

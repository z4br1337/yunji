"""
初始化管理员账户 —— 在 migrate 之后运行
如果管理员已存在但 password_hash 为空，则补充设置密码
"""
import os
import sys
import hashlib
import uuid

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yunji_server.settings')
django.setup()

from api.models import User

admin_username = os.environ.get('ADMIN_USERNAME', 'daoshengzsb0125')
admin_password = os.environ.get('ADMIN_PASSWORD', '123456')

salt = os.environ.get('PASSWORD_SALT', 'yunji_salt_2026')
pw_hash = hashlib.sha256((salt + admin_password).encode('utf-8')).hexdigest()

try:
    user = User.objects.get(username=admin_username)
    if not user.password_hash:
        user.password_hash = pw_hash
        user.save(update_fields=['password_hash'])
        print(f'[init] Admin password_hash was empty, now fixed: {admin_username}')
    else:
        print(f'[init] Admin already exists: {admin_username}')
except User.DoesNotExist:
    User.objects.create(
        openid=uuid.uuid4().hex[:24],
        username=admin_username,
        password_hash=pw_hash,
        nickname='导生',
        role='admin',
        profile_completed=True,
        user_class='管理员',
        exp=100, score=100,
        achievement_counts={},
    )
    print(f'[init] Admin account created: {admin_username}')

"""
初始化管理员账户 —— 在 migrate 之后运行
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

if User.objects.filter(username=admin_username).exists():
    print(f'[init] Admin already exists: {admin_username}')
    sys.exit(0)

salt = os.environ.get('PASSWORD_SALT', 'yunji_salt_2026')
pw_hash = hashlib.sha256((salt + admin_password).encode('utf-8')).hexdigest()

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

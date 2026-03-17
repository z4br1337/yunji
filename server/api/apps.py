from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from django.db import connection
        try:
            tables = connection.introspection.table_names()
            if 'users' not in tables:
                return
            from .models import User
            import hashlib, uuid, os
            admin_username = os.environ.get('ADMIN_USERNAME', 'daoshengzsb0125')
            admin_password = os.environ.get('ADMIN_PASSWORD', '123456')
            if not User.objects.filter(username=admin_username).exists():
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
            else:
                print(f'[init] Admin account already exists: {admin_username}')
        except Exception as e:
            print(f'[init] Skip admin init: {e}')

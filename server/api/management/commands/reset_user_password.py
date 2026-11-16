"""按学号/账号重置指定用户密码的管理命令（运维/超级管理员使用）。

默认只做“干跑”展示匹配账号，不修改数据；加上 --yes 才会执行变更，并写入 AdminActionLog 审计日志。
"""
from django.core.management.base import BaseCommand, CommandError

from api.models import AdminActionLog, User

try:  # 复用后端已有的加密逻辑，与现有账号哈希保持兼容
    from api.views import _hash_password
except Exception:  # pragma: no cover - 仅在极端环境下回退
    import hashlib
    import os

    def _hash_password(password):  # type: ignore[no-redef]
        salt = os.environ.get('PASSWORD_SALT', 'yunji_salt_2026')
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()


class Command(BaseCommand):
    help = '按学号/账号重置用户密码。默认不修改数据，仅展示匹配结果。'

    def add_arguments(self, parser):
        parser.add_argument('--student-id', help='绑定的学号（多个账号绑定同一学号时不生效）')
        parser.add_argument('--username', help='登录账号')
        parser.add_argument('--openid', help='用户 openid')
        parser.add_argument('--password', required=True, help='新密码，至少 6 位')
        parser.add_argument('--yes', action='store_true', help='确认执行变更；否则只做展示')
        parser.add_argument('--dry-run', action='store_true', help='不修改数据，只打印匹配账号')

    def handle(self, *args, **options):
        password = options['password']
        if len(password) < 6:
            raise CommandError('密码长度至少 6 位')

        mode = None
        value = None
        for key in ('student_id', 'username', 'openid'):
            if options[key]:
                if mode:
                    raise CommandError('--student-id / --username / --openid 只能提供一个')
                mode = key
                value = options[key]

        if not mode:
            raise CommandError('请至少提供 --student-id / --username / --openid 之一')

        lookup = {mode: value.strip() if mode == 'student_id' else value}
        users = list(User.objects.filter(**lookup))
        if not users:
            raise CommandError('未找到匹配账号')

        self.stdout.write(f'匹配到 {len(users)} 个账号：')
        for u in users:
            self.stdout.write(
                f"  username={u.username or '(未设置)'} nickname={u.nickname or '(未设置)'} "
                f"openid={u.openid} 班级={u.user_class or '-'} student_id={u.student_id or '-'} role={u.role}"
            )

        if not options['yes'] and not options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    '未传入 --yes，未做任何修改。如需执行重置，请再次运行并加上 --yes。'
                )
            )
            return

        new_hash = _hash_password(password)
        for u in users:
            u.password_hash = new_hash
            u.save(update_fields=['password_hash', 'updated_at'])
            AdminActionLog.objects.create(
                admin_id='cli:reset_user_password',
                action='reset_password',
                target_type='user',
                target_id=str(u.openid),
                detail={'method': mode, 'password_length': len(password), 'by': 'management_command'},
            )
            self.stdout.write(self.style.SUCCESS(f'已重置 openid={u.openid} 的密码'))

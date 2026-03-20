"""邮箱验证码发送（Django send_mail）"""
import random

from django.conf import settings
from django.core.mail import send_mail

CODE_VALID_MINUTES = 15


def generate_numeric_code():
    return f'{random.randint(0, 99999):05d}'


def send_verification_email(email, code):
    subject = '【云迹】邮箱验证码'
    body = (
        f'您的验证码为：{code}，{CODE_VALID_MINUTES} 分钟内有效。\n'
        '如非本人操作，请忽略本邮件。'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@yunji.local'
    send_mail(subject, body, from_email, [email], fail_silently=False)

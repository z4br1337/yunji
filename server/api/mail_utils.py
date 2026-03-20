"""邮箱验证码发送（Django send_mail）"""
import logging
import random
import smtplib
import time

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

CODE_VALID_MINUTES = 15


def generate_numeric_code():
    return f'{random.randint(0, 99999):05d}'


def _smtp_retry_settings():
    retries = max(1, int(getattr(settings, 'EMAIL_SMTP_MAX_RETRIES', 3) or 3))
    delay = float(getattr(settings, 'EMAIL_SMTP_RETRY_DELAY_SEC', 2.0) or 2.0)
    return retries, delay


def send_verification_email(email, code):
    """发送验证码；对 SMTP 连接/超时类错误做有限次重试（适合海外机房跨境 SMTP）。"""
    subject = '【云迹】邮箱验证码'
    body = (
        f'您的验证码为：{code}，{CODE_VALID_MINUTES} 分钟内有效。\n'
        '如非本人操作，请忽略本邮件。'
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'noreply@yunji.local'

    retries, base_delay = _smtp_retry_settings()
    last_error = None

    for attempt in range(retries):
        try:
            send_mail(subject, body, from_email, [email], fail_silently=False)
            if attempt > 0:
                logger.info('send_verification_email succeeded on attempt %s', attempt + 1)
            return
        except smtplib.SMTPResponseException:
            # 认证失败、收件被拒等不应重试
            raise
        except (TimeoutError, ConnectionError, OSError, smtplib.SMTPServerDisconnected) as e:
            last_error = e
            logger.warning(
                'send_mail attempt %s/%s failed (%s): %s',
                attempt + 1,
                retries,
                type(e).__name__,
                e,
            )
            if attempt < retries - 1:
                time.sleep(base_delay * (attempt + 1))

    if last_error is not None:
        raise last_error

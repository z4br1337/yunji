import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 持久化数据目录：部署时挂载 Volume 到 /data，升级版本后数据可保留
# 本地开发时使用 BASE_DIR，Docker 部署时使用 /data
DATA_DIR = Path(os.environ.get('DATA_DIR', str(BASE_DIR)))
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'api.middleware.AuthMiddleware',
    'api.middleware.StudentIdRequiredMiddleware',
]

ROOT_URLCONF = 'yunji_server.urls'
APPEND_SLASH = False

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite')

if DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.environ.get('MYSQL_ADDRESS', '127.0.0.1:3306').split(':')[0],
            'PORT': int(os.environ.get('MYSQL_ADDRESS', '127.0.0.1:3306').split(':')[-1]),
            'NAME': os.environ.get('MYSQL_DATABASE', 'yunji'),
            'USER': os.environ.get('MYSQL_USERNAME', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(DATA_DIR / 'db.sqlite3'),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


MEDIA_URL = '/media/'
MEDIA_ROOT = DATA_DIR / 'media'

UPLOAD_MAX_SIZE_MB = 10

# 邮件（找回密码 / 绑定邮箱）。DEBUG=True 默认打印到控制台；生产请配置 SMTP 环境变量
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
# 465 端口一般为 SSL：设 EMAIL_USE_SSL=true 且 EMAIL_USE_TLS=false
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'false').lower() == 'true'
# 东京等海外机房连国内 SMTP 易超时，默认拉长超时；可通过环境变量调整
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '45'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@yunji.local')
# 发送验证码时的重试（仅 api.mail_utils 使用，缓解偶发网络抖动）
EMAIL_SMTP_MAX_RETRIES = max(1, int(os.environ.get('EMAIL_SMTP_MAX_RETRIES', '3')))
EMAIL_SMTP_RETRY_DELAY_SEC = float(os.environ.get('EMAIL_SMTP_RETRY_DELAY_SEC', '2'))

FRONTEND_DIR = Path(os.environ.get('FRONTEND_DIR', str(BASE_DIR.parent / 'webapp' / 'dist')))

"""
统一中间件：鉴权 + API 异常保护
"""
import traceback
from django.http import JsonResponse
from django.utils import timezone

from .models import User
from .constants import is_super_admin_user

# 未绑定学号时仍可调用的接口（相对路径，不含 /api/ 前缀）
_STUDENT_EXEMPT_SUBPATHS = frozenset({
    'user/login',
    'user/register',
    'user/bind-student-id',
})

# 账号已封禁/已注销时仍可调用的接口（与登录相关）
_ACCOUNT_STATUS_EXEMPT_SUBPATHS = frozenset({
    'user/login',
    'user/register',
    'user/bind-student-id',
})


class AccountBannedMiddleware:
    """已封禁或已注销账号禁止使用业务接口（登录页可感知错误）。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ''
        if path.startswith('/api/'):
            sub = path[len('/api/'):]
            if sub in _ACCOUNT_STATUS_EXEMPT_SUBPATHS:
                return self.get_response(request)
            token = getattr(request, 'user_token', '') or ''
            if token:
                try:
                    user = User.objects.get(openid=token)
                except User.DoesNotExist:
                    return self.get_response(request)
                now = timezone.now()
                if getattr(user, 'account_deleted', False):
                    return JsonResponse({
                        'code': 'ACCOUNT_GONE',
                        'message': '账号已注销',
                        'data': {},
                    }, status=403)
                bu = getattr(user, 'banned_until', None)
                if bu and now < bu:
                    return JsonResponse({
                        'code': 'ACCOUNT_BANNED',
                        'message': '账号已被封禁，暂无法使用',
                        'data': {},
                    }, status=403)
        return self.get_response(request)


class StudentIdRequiredMiddleware:
    """除白名单外，已登录用户须已绑定学号才可调用业务接口（超级管理员除外）"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or ''
        if path.startswith('/api/'):
            sub = path[len('/api/'):]
            if sub in _STUDENT_EXEMPT_SUBPATHS:
                return self.get_response(request)
            token = getattr(request, 'user_token', '') or ''
            if token:
                try:
                    user = User.objects.get(openid=token)
                except User.DoesNotExist:
                    return self.get_response(request)
                if not is_super_admin_user(user):
                    if not (user.student_id or '').strip():
                        return JsonResponse({
                            'code': 'STUDENT_ID_REQUIRED',
                            'message': '请先绑定学号',
                            'data': {},
                        })
        return self.get_response(request)


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = ''
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth.startswith('Bearer '):
            token = auth[7:].strip()
        request.user_token = token

        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            if request.path.startswith('/api/'):
                traceback.print_exc()
                return JsonResponse({
                    'code': 'SERVER_ERROR',
                    'message': f'服务器内部错误: {str(e)}',
                    'data': {}
                }, status=500)
            raise

"""
统一中间件：鉴权 + API 异常保护
"""
import traceback
from django.http import JsonResponse

from .models import User
from .constants import is_super_admin_user

# 未绑定学号时仍可调用的接口（相对路径，不含 /api/ 前缀）
_STUDENT_EXEMPT_SUBPATHS = frozenset({
    'user/login',
    'user/register',
    'user/bind-student-id',
})


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

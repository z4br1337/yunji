"""
统一中间件：鉴权 + API 异常保护
"""
import traceback
from django.http import JsonResponse


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

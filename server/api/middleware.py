"""
统一鉴权中间件
从请求 header Authorization: Bearer <token> 中提取用户标识
"""


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = ''
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth.startswith('Bearer '):
            token = auth[7:].strip()
        request.user_token = token
        return self.get_response(request)

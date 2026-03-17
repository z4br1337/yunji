import os
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, FileResponse, Http404


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'yunji-api'})


def serve_frontend(request, path=''):
    """SPA fallback: serve Vue frontend from dist/"""
    frontend_dir = getattr(settings, 'FRONTEND_DIR', None)
    if not frontend_dir or not os.path.isdir(frontend_dir):
        return JsonResponse({'error': 'Frontend not built'}, status=404)

    file_path = os.path.join(frontend_dir, path)
    if path and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))

    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.isfile(index_path):
        return FileResponse(open(index_path, 'rb'), content_type='text/html')

    raise Http404


urlpatterns = [
    path('healthz', health_check),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^(?P<path>.*)$', serve_frontend),
]

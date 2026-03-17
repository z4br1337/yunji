import os
import mimetypes
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, FileResponse, Http404

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

CACHE_EXTENSIONS = {'.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.woff', '.woff2', '.ttf', '.ico'}


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'yunji-api'})


def serve_frontend(request, path=''):
    frontend_dir = getattr(settings, 'FRONTEND_DIR', None)
    if not frontend_dir or not os.path.isdir(str(frontend_dir)):
        return JsonResponse({'error': 'Frontend not built'}, status=404)

    file_path = os.path.join(str(frontend_dir), path)
    if path and os.path.isfile(file_path):
        resp = FileResponse(open(file_path, 'rb'))
        ext = os.path.splitext(path)[1].lower()
        if ext in CACHE_EXTENSIONS:
            resp['Cache-Control'] = 'public, max-age=31536000, immutable'
        return resp

    index_path = os.path.join(str(frontend_dir), 'index.html')
    if os.path.isfile(index_path):
        resp = FileResponse(open(index_path, 'rb'), content_type='text/html')
        resp['Cache-Control'] = 'no-cache'
        return resp

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

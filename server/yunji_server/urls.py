import hashlib
import os
import mimetypes
from pathlib import Path
from django.urls import path, include, re_path
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404

try:
    from PIL import Image
except ImportError:
    Image = None

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

CACHE_EXTENSIONS = {'.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.woff', '.woff2', '.ttf', '.ico'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico'}
THUMB_RASTER_EXT = {'.png', '.jpg', '.jpeg', '.webp'}
# 列表缩略图最长边（像素），减小传输体积
FEED_THUMB_MAX_EDGE = 280


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'yunji-api'})


def _safe_media_path(path):
    root = Path(settings.MEDIA_ROOT).resolve()
    candidate = (root / path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return str(candidate) if candidate.is_file() else None


def _ensure_feed_thumbnail(original_abs, max_edge):
    """生成并返回缩略图绝对路径；失败则返回 None。"""
    if not Image or not original_abs or not os.path.isfile(original_abs):
        return None
    ext = Path(original_abs).suffix.lower()
    if ext not in THUMB_RASTER_EXT:
        return None
    root = Path(settings.MEDIA_ROOT).resolve()
    digest = hashlib.sha256(original_abs.encode('utf-8')).hexdigest()[:20]
    cache_dir = root / '.thumb_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / f'{digest}_{max_edge}.jpg'
    try:
        src_mtime = os.path.getmtime(original_abs)
    except OSError:
        return None
    if out_path.is_file() and out_path.stat().st_mtime >= src_mtime:
        return str(out_path)
    try:
        with Image.open(original_abs) as im:
            if im.mode in ('RGBA', 'LA'):
                bg = Image.new('RGB', im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            elif im.mode != 'RGB':
                im = im.convert('RGB')
            im.thumbnail((max_edge, max_edge))
            im.save(out_path, 'JPEG', quality=82, optimize=True)
    except Exception:
        if out_path.is_file():
            try:
                out_path.unlink()
            except OSError:
                pass
        return None
    return str(out_path)


def serve_media(request, path=''):
    """Serve user-uploaded media files with caching headers. ?thumb=feed 返回列表用缩略图。"""
    file_path = _safe_media_path(path)
    if not file_path:
        raise Http404
    ext = os.path.splitext(path)[1].lower()
    want_thumb = (request.GET.get('thumb') or '').strip().lower() == 'feed'

    if want_thumb and ext in THUMB_RASTER_EXT:
        thumb_abs = _ensure_feed_thumbnail(file_path, FEED_THUMB_MAX_EDGE)
        if thumb_abs:
            resp = FileResponse(open(thumb_abs, 'rb'), content_type='image/jpeg')
            resp['Cache-Control'] = 'public, max-age=604800'
            return resp
        # Pillow 不可用或处理失败时回退原图
    resp = FileResponse(open(file_path, 'rb'))
    if ext in IMAGE_EXTENSIONS:
        resp['Cache-Control'] = 'public, max-age=604800'
    else:
        resp['Cache-Control'] = 'public, max-age=86400'
    return resp


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
        resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp['Pragma'] = 'no-cache'
        resp['Expires'] = '0'
        return resp

    raise Http404


urlpatterns = [
    path('healthz', health_check),
    path('api/', include('api.urls')),
    re_path(r'^media/(?P<path>.+)$', serve_media),
]

urlpatterns += [
    re_path(r'^(?P<path>.*)$', serve_frontend),
]

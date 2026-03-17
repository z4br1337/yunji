#!/bin/sh
set -e

echo "[start] Running migrations..."
python manage.py migrate --noinput 2>&1

echo "[start] Initializing admin account..."
python init_admin.py 2>&1 || true

echo "[start] Collecting static files..."
python manage.py collectstatic --noinput 2>&1 || true

echo "[start] Starting gunicorn on port ${PORT:-8080}..."
exec gunicorn yunji_server.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

#!/bin/sh
set -e

mkdir -p /data/media

echo "[boot] Running migrate..."
python manage.py migrate --noinput --run-syncdb

echo "[boot] Creating admin..."
python init_admin.py || true

echo "[boot] Collecting static..."
python manage.py collectstatic --noinput || true

echo "[boot] Starting gunicorn on port ${PORT:-8080}..."
exec gunicorn yunji_server.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 --access-logfile - --error-logfile -

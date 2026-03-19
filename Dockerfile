# ---- Stage 1: Build Vue Frontend ----
FROM node:18-slim AS frontend
WORKDIR /build
COPY webapp/package.json webapp/package-lock.json* ./
RUN npm ci --no-audit --no-fund 2>/dev/null || npm install --no-audit --no-fund
COPY webapp/ ./
RUN npm run build

# ---- Stage 2: Python Backend ----
FROM python:3.11-slim
WORKDIR /app

ENV DB_ENGINE=sqlite
ENV FRONTEND_DIR=/webapp/dist
ENV DJANGO_SETTINGS_MODULE=yunji_server.settings
# 持久化目录：在 Zeabur 控制台挂载 Volume 到 /data，升级版本后数据可保留
ENV DATA_DIR=/data

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

RUN mkdir -p /webapp/dist /app/staticfiles
COPY --from=frontend /build/dist /webapp/dist

# Create entrypoint: 使用 /data 存储数据库和媒体，支持 Volume 持久化
RUN printf '#!/bin/sh\nset -e\nmkdir -p /data/media\necho "[boot] Running migrate..."\npython manage.py migrate --noinput --run-syncdb\necho "[boot] Creating admin..."\npython init_admin.py || true\necho "[boot] Collecting static..."\npython manage.py collectstatic --noinput || true\necho "[boot] Starting gunicorn on port ${PORT:-8080}..."\nexec gunicorn yunji_server.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 --access-logfile - --error-logfile -\n' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

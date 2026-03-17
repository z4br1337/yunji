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

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

RUN mkdir -p /webapp/dist
COPY --from=frontend /build/dist /webapp/dist

EXPOSE 8080

CMD python manage.py migrate --noinput && python init_admin.py ; python manage.py collectstatic --noinput 2>/dev/null ; exec gunicorn yunji_server.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 --access-logfile - --error-logfile -

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

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

# Copy frontend build output to a location FRONTEND_DIR can find
RUN mkdir -p /webapp/dist
COPY --from=frontend /build/dist /webapp/dist

RUN python manage.py collectstatic --noinput 2>/dev/null || true
RUN DB_ENGINE=sqlite python manage.py migrate --noinput 2>/dev/null || true

ENV PORT=8080
ENV FRONTEND_DIR=/webapp/dist
ENV DB_ENGINE=sqlite
EXPOSE 8080

CMD gunicorn yunji_server.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --timeout 120

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

# 使用 /data 存储数据库和媒体，支持 Volume 持久化
COPY server/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh 2>/dev/null || true && chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

# 云迹 — Railway 部署适配指南

本项目已适配 **Railway**（类似 Zeabur 的 PaaS，直接从 GitHub 部署，自动分配域名与 HTTPS）。

适配要点：
- 项目根目录已有 `Dockerfile`（多阶段：先编译 Vue 前端，再打入 Django 后端），Railway 会自动构建。
- 容器内 gunicorn 监听 `$PORT`（Railway 自动注入），`/healthz` 做健康检查。
- 数据库与上传文件用 **持久化 Volume**，挂载到容器内的 `/data`（Railway 面板添加），升级/重新部署后数据不丢失。
- `docker-compose.yml` / `nginx/`（原腾讯云方案）已移除，Railway 不需要。

---

## 一、在 Railway 创建服务

1. 将本项目推送到 GitHub 仓库（或确认已推送）。
2. 打开 Railway Dashboard → **New Project** → **Deploy from GitHub repo** → 选择该仓库。
3. Railway 检测到 `Dockerfile`，自动用 Docker 构建并部署。
4. 部署完成后，在 **Settings → Networking** 里点 **Generate Domain**，得到类似 `yunji-xxxx.up.railway.app` 的公网域名（自带 HTTPS）。
5. 访问 `https://<域名>/healthz`，应返回 `{"status":"ok","service":"yunji-api"}`。

---

## 二、添加持久化数据卷（关键）

Railway 默认容器文件系统是临时的，重新部署会清空数据。**必须**挂载 Volume，否则数据库和用户上传的图片/文件会丢失。

在 Railway Dashboard：
1. 进入该服务的 **Settings** → **Volumes**。
2. 点 **New Volume**，挂载路径填 `/data`，名称填 `yunji-data`。
3. 保存，Railway 会重启容器并将 Volume 挂载到容器内 `/data`。

之后：
- SQLite 数据库存放于 `/data/db.sqlite3`
- 用户上传的头像/帖子图片/分享文件存放于 `/data/media/`
- 无论多少次重新部署，`/data` 内容都会保留。

---

## 三、配置环境变量

在 Railway Dashboard 的 **Variables** 页面添加（按需填写）：

| 变量 | 说明 | 推荐值 |
|------|------|--------|
| `DJANGO_SECRET_KEY` | Django 安全密钥，生产必须替换 | 随机长字符串 |
| `ADMIN_USERNAME` | 超级管理员账号 | `daoshengzsb0125` |
| `ADMIN_PASSWORD` | 超级管理员密码 | 自定义 |
| `PASSWORD_SALT` | 密码哈希加盐 | `yunji_salt_2026`（与旧数据兼容） |
| `DATA_DIR` | 持久化数据目录 | `/data` |
| `DEBUG` | 调试开关 | `False` |
| `ALLOWED_HOSTS` | 允许的主机 | `*`（或填 Railway 域名） |

Railway 会自动注入 `PORT`（如 `8080`），**不需要**手动设置；entrypoint.sh 里的 gunicorn 会读取 `$PORT`。

> `PORT`、`FRONTEND_DIR=/webapp/dist`、`DB_ENGINE=sqlite`、`DJANGO_SETTINGS_MODULE` 已在 Dockerfile / entrypoint 中设定，通常无需再写。

---

## 四、部署并验证

1. 变更环境变量或 Volume 后，Railway 会自动重新部署。
2. 部署完成后打开生成的域名，用 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 登录。
3. 如要查看后端日志：Railway Dashboard → 该服务 → **Deployments** → 点某次部署 → **Logs**。

---

## 五、把旧数据（Zeabur/本地备份）导入到 Railway

你之前已在本地生成了：
- `D:\YUNJI BACKUP\latest.json`（全量数据 JSON：users 296 / posts 122 / comments 87 / achievements 14 / points_log 169 / messages 23）
- `server\media\`（241 个媒体文件）

Railway 没有直接的文件上传入口，推荐通过 **Railway CLI** 把数据导进容器。

### 5.1 安装并登录 Railway CLI

```bash
# Windows (PowerShell)
iwr https://railway.app/install.ps1 -useb | iex

# 验证
railway --version
```

```bash
railway login
# 按提示在浏览器授权，完成后
railway link   # 选择你的云迹项目/服务
```

### 5.2 把备份文件传到 Railway 容器

Railway 容器内的持久化卷在 `/data`。你可以先把 `latest.json` 放到一个临时可公开下载的地方（例如 0x0.st、文件传输服务、或自己的 GitHub Release），得到一个直链。

然后用 Railway CLI 进容器 shell 下载并导入：

```bash
# 进入运行中服务的容器 shell
railway ssh

# 在容器内（示例，把 <直链> 换成你的 latest.json 直链）：
curl -L -o /tmp/latest.json <latest.json 直链>

# 导入数据（会清空当前表并重新导入，所有账号密码重置为 123456）
python import_backup.py /tmp/latest.json

# 如需把旧服务器的 media 也一起拉下来（旧服务器仍在线时）：
python import_backup.py /tmp/latest.json --media-base https://yunji.zeabur.app

exit
```

`--media-base` 会把 JSON 里引用的全部 `/media/...` 文件从旧服务器下载到 `/data/media/`，失败的文件会跳过并打印。

导入成功后，输出应显示：
```
Import done.
  users: 296
  posts: 122
  comments: 87
  achievements: 14
  points_log: 169
  messages: 23
```

如果旧服务器已下线，media 文件需另行从本地 `server\media\` 上传（可把 media 打包 tar 放到临时直链，容器内 `curl` 下载后 `tar -xzf - -C /data/media`）。

---

## 六、后续更新代码

```bash
git push origin main   # 推到 GitHub
# Railway 检测到仓库变更，自动重新构建并部署
# /data Volume 保留，数据不会丢
```

---

## 七、常见问题

| 问题 | 处理 |
|------|------|
| 重新部署后数据没了 | 没挂载 Volume 到 `/data`；到 Dashboard 添加 Volume |
| 打不开网站 / 502 | 查看 Deployments 日志；确认 gunicorn 监听 `$PORT` |
| 登录报错 / 找不到管理员 | 确认已设置 `ADMIN_USERNAME`、`ADMIN_PASSWORD`，且已重新部署 |
| 图片打不开 | 媒体文件需挂载 Volume 且 media 下载到 `/data/media` |
| 需要 HTTPS | Railway 自动提供，无需配置 |

---

## 文件清单（本次适配新增）

| 文件 | 说明 |
|------|------|
| `railway.toml` | Railway 构建/部署配置（Dockerfile、健康检查 `/healthz`） |
| `server/import_backup.py` | 增加 URL 备份读入与 `--media-base` 远程拉取媒体文件 |
| `deploy_railway.md` | 本部署指南 |

原 `server/entrypoint.sh`、`Dockerfile`、`server/yunji_server/settings.py` 已适配 `DATA_DIR=/data`，无需修改。

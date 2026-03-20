# 云迹 Web 版部署指南

## 版本更新后网站仍显示旧内容？

### 可能原因与处理步骤

#### 1. Zeabur 未自动重新部署

**检查与手动触发：**

1. 登录 [Zeabur 控制台](https://zeabur.com)
2. 进入项目，找到云迹服务
3. 查看 **Deployments** 或 **构建历史**，确认最新一次构建是否在最近 push 之后
4. 若未自动构建，点击 **「Redeploy」** 或 **「重新部署」** 手动触发
5. 等待构建完成（约 2–5 分钟）

**确认 GitHub 已正确连接：**

- 控制台 → **Settings** → **Integrations** → 确认已连接 GitHub
- 在对应仓库中已安装 Zeabur GitHub App
- 服务设置中的 **Watch Paths** 为 `*` 或包含 `webapp/`、`server/`（默认会监听所有变更）

#### 2. 浏览器 / PWA 缓存

即使服务器已更新，本地缓存仍可能显示旧版：

1. **强制刷新**：`Ctrl + Shift + R`（Windows）或 `Cmd + Shift + R`（Mac）
2. **清除站点数据**：
   - Chrome：地址栏左侧锁图标 → 网站设置 → 清除数据
   - 或：开发者工具 (F12) → Application → Storage → Clear site data
3. **关闭所有该网站标签页** 后重新打开

#### 3. 代码与构建

- 确认修改已 `git push` 到 GitHub 的 `main` 分支
- 若使用其他分支，需在 Zeabur 中配置部署分支

---

## 数据持久化（重要：升级版本后保留数据）

部署到 Zeabur 时，**必须挂载持久化卷**，否则每次升级版本后数据库和上传文件会被清空。

### Zeabur 挂载步骤

1. 打开 Zeabur 控制台，进入你的云迹服务
2. 点击 **「Volumes」** 标签
3. 点击 **「Mount Volumes」**
4. 在 **Mount Directory** 中填写：`/data`
5. **Volume ID** 可填写：`yunji-data`
6. 保存并重新部署

挂载后，数据库（`db.sqlite3`）和用户上传的图片/文件（`media/`）将存储在 Volume 中，**升级版本后数据会保留**。

### 首次挂载说明

- **新部署**：直接按上述步骤挂载即可
- **已有数据**：首次挂载时 Volume 为空，原有容器内数据会丢失。若需迁移，请先在 Zeabur 控制台进入容器终端，将 `/app` 下的数据备份后再挂载

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATA_DIR` | 持久化数据目录 | `/data`（Docker） |
| `DJANGO_SECRET_KEY` | Django 密钥 | 建议生产环境设置 |
| `DB_ENGINE` | 数据库类型 | `sqlite` |
| `MYSQL_*` | MySQL 连接（当 DB_ENGINE=mysql 时） | - |
| `EMAIL_BACKEND` | Django 邮件后端 | `DEBUG=true` 时为控制台输出；生产一般为 SMTP |
| `EMAIL_HOST` / `EMAIL_PORT` | SMTP 服务器 | 生产发信必填（找回密码、绑定邮箱） |
| `EMAIL_USE_TLS` | 是否 TLS | 默认 `true` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP 账号密码 | 视服务商要求 |
| `DEFAULT_FROM_EMAIL` | 发件人地址 | 默认同 `EMAIL_HOST_USER` 或占位值 |

> **找回密码 / 绑定邮箱** 依赖邮件发送。部署到 Zeabur 等环境时，请配置上述 SMTP 相关变量；未配置时接口会返回「邮件发送失败」类错误。

---

## 本地开发

本地开发时无需挂载 Volume，数据存储在项目目录下，与部署环境隔离。

---

## 前端缓存（PWA）

应用已启用 Service Worker 缓存：

- **首次访问**：正常加载并缓存静态资源（JS、CSS、图片等）
- **再次访问**：优先从本地缓存加载，加快打开速度
- **版本更新**：自动检测并更新缓存，无需用户操作

用户首次使用后，页面资源会保存在设备本地，后续访问加载更快。

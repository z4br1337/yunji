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
| `EMAIL_HOST` / `EMAIL_PORT` | SMTP 服务器 | 当前主流程为**学号绑定/登录**，邮件变量仅在你自行扩展发信功能时需要 |
| `EMAIL_USE_TLS` | 是否 STARTTLS（常见于 587） | 默认 `true` |
| `EMAIL_USE_SSL` | 是否 SSL 直连（常见于 465） | 默认 `false`；为 `true` 时一般需 `EMAIL_USE_TLS=false` |
| `EMAIL_TIMEOUT` | SMTP 连接/读写超时（秒） | 默认 `45`（海外机房建议 `60`～`90`） |
| `EMAIL_SMTP_MAX_RETRIES` | 验证码邮件发送失败时的重试次数 | 默认 `3` |
| `EMAIL_SMTP_RETRY_DELAY_SEC` | 重试基础间隔（秒，会按次数递增） | 默认 `2` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP 账号密码 | 视服务商要求 |
| `DEFAULT_FROM_EMAIL` | 发件人地址 | 默认同 `EMAIL_HOST_USER` 或占位值 |

> 产品端已改为 **绑定学号** 与 **用户名/学号登录**，不再依赖邮件验证码。若你 fork 后自行加回邮件能力，可继续配置上述 SMTP 变量。

### 服务器在海外（如东京）发信超时怎么办？

跨境连接 **QQ / 163 等国内 SMTP** 经常出现 **连接超时或极慢**，仅靠加长超时无法根本解决，建议按优先级处理：

1. **推荐：换用全球/亚太有节点的发信服务（SMTP 与服务器同区域或就近）**  
   例如 **Amazon SES**（可选 `ap-northeast-1` 东京）、**Resend**、**SendGrid**、**Mailgun** 等，在控制台开启 SMTP 后，把 `EMAIL_HOST` 填成服务商提供的 **就近 SMTP 主机名**，超时问题通常会消失。

2. **仍使用国内邮箱 SMTP 时，可尝试**  
   - 将 `EMAIL_TIMEOUT` 设为 **`60` 或 `90`**。  
   - 部分邮箱 **465 + SSL** 比 **587 + TLS** 更稳定，可尝试：  
     `EMAIL_PORT=465`、`EMAIL_USE_SSL=true`、`EMAIL_USE_TLS=false`（以邮箱官方文档为准）。  
   - 若仍频繁超时，说明链路质量差，应改用第 1 种方案。

3. **代码侧已做优化**  
   对 **网络类错误**（超时、断连等）会自动 **重试若干次**（见上表 `EMAIL_SMTP_*`），减轻偶发抖动；**认证失败（如密码错误）不会重试**。

### Postmark 配置步骤（与云迹 SMTP 对接）

云迹使用 Django 标准 `send_mail`，**无需改代码**，在 Postmark 完成发件人验证后，在 Zeabur（或本地）配置以下环境变量即可。

#### 1. 注册与创建 Server

1. 打开 [Postmark](https://postmarkapp.com) 注册并登录。  
2. 创建一个 **Server**（可命名为 `yunji`）。每个 Server 对应一套发信配置与统计。

#### 2. 验证发件域名或发件邮箱（必做）

Postmark **只允许已验证的发件地址** 发信：

- **推荐**：在 **Sender Signatures** 验证你的域名（如 `yourdomain.com`），之后可用 `noreply@yourdomain.com` 等任意该域地址作为发件人。  
- **或**：先添加并验证单个 **邮箱地址**（会收到验证邮件），用于测试。

未验证的地址会导致发送被拒（错误信息里会说明）。

#### 3. 获取 SMTP 凭据

1. 进入该 **Server** → **API Tokens**（或设置中的 API / SMTP 说明页）。  
2. 复制 **Server API Token**（**不是** Account API Token）。  
3. Postmark SMTP 规则（Transactional 事务邮件）：  
   - **主机**：`smtp.postmarkapp.com`  
   - **端口**：`587`，启用 **STARTTLS**（与云迹默认 `EMAIL_USE_TLS=true` 一致）  
   - **用户名**：填 **Server API Token**  
   - **密码**：再填 **同一串 Server API Token**（用户名与密码相同，这是 Postmark 官方用法）

> 若使用 **SMTP Token**（在 Outbound Stream 里生成的 Access Key / Secret Key），则用户名为 Access Key、密码为 Secret Key；一般直接用 Server API Token 即可。

#### 4. 在云迹（Zeabur）中填写环境变量

在跑 Django 的服务里新增/修改变量（示例值请换成你自己的）：

| 变量 | 示例 / 说明 |
|------|-------------|
| `EMAIL_BACKEND` | 可不设；生产 `DEBUG=false` 时默认已是 SMTP |
| `EMAIL_HOST` | `smtp.postmarkapp.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `true` |
| `EMAIL_USE_SSL` | `false` |
| `EMAIL_HOST_USER` | 你的 **Server API Token** |
| `EMAIL_HOST_PASSWORD` | **同上**（与 USER 完全一致） |
| `DEFAULT_FROM_EMAIL` | 已在 Postmark 验证过的发件邮箱，如 `noreply@yourdomain.com` |
| `EMAIL_TIMEOUT` | 可选 `30`～`60`（Postmark 通常较快） |

保存后 **重新部署** 服务。

#### 5. 自测

在 Postmark 后台 **Activity** 查看是否入队、是否被拒及原因（需在你自行接入发信代码后才有流量）。

#### 6. 常见问题

- **发件人被拒**：检查 `DEFAULT_FROM_EMAIL` 是否在 Postmark 里已验证（域名或单邮箱）。  
- **认证失败**：确认用的是 **Server API Token**，且 USER / PASSWORD 均为同一 Token。  
- **广播类邮件**：若将来走 Broadcast Stream，SMTP 主机可能为 `smtp-broadcasts.postmarkapp.com`；云迹验证码属 **Transactional**，用 `smtp.postmarkapp.com` 即可。

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

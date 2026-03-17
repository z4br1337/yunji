# 云迹 —— 基于微信云开发的校园社交互动小程序

> 云迹是一款面向校园学生的社交互动微信小程序，支持匿名情感倾诉、成果展示（德智体美劳）与积分激励、管理员（导生）审核与评分等功能，基于微信小程序原生框架 + 微信云开发构建。

---

## 目录

- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [功能架构](#功能架构)
- [云开发配置](#云开发配置)
- [数据集合说明](#数据集合说明)
- [审核 API Key 设置](#审核-api-key-设置)
- [邀请码生成与验证流程](#邀请码生成与验证流程)
- [积分规则](#积分规则)
- [本地调试与测试](#本地调试与测试)
- [数据迁移与兼容说明](#数据迁移与兼容说明)
- [部署步骤](#部署步骤)

---

## 项目结构

```
yunji/
├── miniprogram/                          # 小程序前端
│   ├── app.js / app.json / app.wxss      # 全局入口、路由、样式
│   ├── config/index.js                   # 前端配置入口
│   ├── utils/
│   │   ├── api.js                        # 云函数调用统一封装（重试/超时/错误码）
│   │   └── config.js                     # 常量配置（积分规则/分类/状态/feature flags）
│   ├── pages/
│   │   ├── login/                        # 微信一键登录
│   │   ├── profile-edit/                 # 个人资料编辑（必填）
│   │   ├── feed/                         # 帖子信息流（含情感入口）
│   │   ├── post-create/                  # 发帖（文字+图片+匿名）
│   │   ├── post-detail/                  # 帖子详情+评论+管理操作
│   │   ├── achievements/                 # 成果展示（德智体美劳）
│   │   ├── achievement-create/           # ★ 成果提交页
│   │   ├── emotion-help/                 # ★ 情感倾诉专线（匿名联系导生）
│   │   ├── settings/                     # ★ 个人中心（邀请码/积分/管理入口）
│   │   └── admin/
│   │       ├── dashboard/                # 管理后台（审核/用户/邀请码）
│   │       └── user-profile/             # ★ 管理员查看用户资料+评分
│   ├── components/
│   │   ├── PostCard/                     # 帖子卡片组件
│   │   └── ProfileForm/                  # 资料表单组件
│   └── images/                           # 静态图片资源
├── cloudfunctions/                       # 云函数（10 个）
│   ├── createPost/                       # 创建帖子
│   ├── getPosts/                         # 获取帖子列表
│   ├── moderatePost/                     # AI 审核适配层
│   ├── updateProfile/                    # 用户资料管理
│   ├── useInviteCode/                    # 邀请码验证
│   ├── addPoints/                        # 积分操作（原子）
│   ├── addComment/                       # ★ 独立评论云函数
│   ├── createAchievement/                # ★ 成果提交
│   ├── getAchievements/                  # ★ 成果列表
│   └── adminActions/                     # 管理员操作集合（12 个 action）
├── tests/cloudfunctions/                 # 单元测试
├── docs/
│   ├── data-models.json                  # 数据模型定义
│   └── sample-data.json                  # 示例数据
├── project.config.json
└── README.md
```

---

## 快速开始

### 环境要求

- [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- Node.js >= 16、npm >= 8

### 初始化步骤

1. 克隆/下载项目到本地。
2. 微信开发者工具 → 导入项目 → 选择 `yunji/` 根目录。
3. 在 `project.config.json` 中填写 **AppID**。
4. 开通云开发 → 创建环境（如 `yunji-prod`）。
5. 修改 `miniprogram/utils/config.js` 中的 `CLOUD_ENV_ID`。
6. 在云开发控制台创建 7 个集合：`users`、`posts`、`comments`、`achievements`、`invites`、`points_log`、`admin_logs`。
7. 部署所有云函数（右键每个目录 → 上传并部署）。
8. 编译运行。

---

## 功能架构

### 用户端

| 功能 | 说明 |
|---|---|
| 微信一键登录 | 自动创建用户，未填资料强制跳转 |
| 个人资料编辑 | nickname + class 必填，完成后解锁所有功能 |
| 发帖（实名/匿名） | 文字+多图，可选匿名+通知导生 |
| 情感倾诉专线 | 匿名模式直接联系导生，优先审核 |
| 成果展示 | 按德智体美劳五类展示，等级+积分 |
| 成果提交 | 选类别/等级/图片，自动计算积分 |
| 积分系统 | 发帖/成果/评分多维度积分 |
| 个人中心 | 资料/积分明细/邀请码/管理员入口 |

### 管理员（导生）端

| 功能 | 说明 |
|---|---|
| 待审核列表 | 快速通过/封存/改分类，支持批量操作 |
| 情感求助 | 优先标记，导生快速对接 |
| 用户管理 | 搜索用户、查看资料、发帖记录、积分日志 |
| 用户评分 | 对用户资料评分 → 触发积分（评分×2） |
| 查看真实作者 | 匿名帖可查看真实身份 |
| 邀请码管理 | 生成/复制邀请码 |
| 修改帖子分类 | 调整帖子的分区归属 |

---

## 云开发配置

### 环境变量

| 变量名 | 说明 | 位置 |
|---|---|---|
| `MODERATION_API_KEY` | 内容审核 API 密钥 | 云函数环境变量 |
| `MODERATION_API_URL` | 内容审核 API 地址 | 云函数环境变量 |
| `CLOUD_ENV_ID` | 云环境 ID | `miniprogram/utils/config.js` |

> **安全要求**：所有敏感信息通过环境变量设置，代码中仅使用 `process.env.XXX` 占位。

---

## 数据集合说明

| 集合 | 用途 | 关键索引建议 |
|---|---|---|
| `users` | 用户信息 | `openid`（唯一） |
| `posts` | 帖子 | `status` + `createdAt`（组合） |
| `comments` | 评论 | `postId` + `createdAt` |
| `achievements` | 成果 | `userId` + `category` |
| `invites` | 邀请码 | `code`（唯一） |
| `points_log` | 积分日志 | `userId` + `createdAt` |
| `admin_logs` | 管理操作日志 | `adminOpenid` + `createdAt` |

详细字段定义见 `docs/data-models.json`。

---

## 审核 API Key 设置

1. 注册第三方审核服务（百度内容审核 / 阿里绿网 / 腾讯天御）。
2. 获取 API Key 和 API URL。
3. 在云函数环境变量设置 `MODERATION_API_KEY` 和 `MODERATION_API_URL`。
4. 修改 `cloudfunctions/moderatePost/config/moderation.js`：
   - 取消 `callContentModeration()` 中真实 API 调用的注释。
   - 实现 `mapVendorVerdict()` 映射函数。

> 当前默认使用 **mock 审核**（全部通过），替换真实 API 只需修改上述单个文件。

---

## 邀请码生成与验证流程

### 生成

- **方式 A**：管理后台 → 邀请码 Tab → 点击「生成新邀请码」。
- **方式 B**：云开发控制台手动在 `invites` 集合添加：
  ```json
  { "code": "INVITE2026A", "role": "admin", "usedBy": null }
  ```

### 验证

1. 用户进入「我的」→ 输入邀请码。
2. 前端调用 `useInviteCode` → 原子更新（防并发）→ 提升 role。
3. 界面刷新，显示管理员入口。

---

## 积分规则

| 动作 | 积分 | 说明 |
|---|---|---|
| 发帖审核通过 | +5 | 自动发放 |
| 提交成果（基础） | +10 | 任何类别 |
| 成果等级加成 | +level × 5 | Lv1=+5, Lv3=+15, Lv5=+25 |
| 管理员评分 | +score × 2 | 评分 50 → +100 积分 |
| 帖子违规封存 | -10 | 已发布帖子被封存时 |
| 每日登录 | +1 | TODO: 待实现 |

> 积分规则定义在 `miniprogram/utils/config.js` → `POINTS_RULES`。
> 积分不允许为负数（扣至 0 为止）。

---

## 本地调试与测试

### 微信开发者工具调试

1. 导入项目 → 开启云函数本地调试。
2. 走完完整流程：登录 → 资料 → 发帖 → 审核 → 成果提交。

### 运行单元测试

```bash
cd tests
npm install
npm test                          # 运行所有测试
npx jest cloudfunctions/createPost.test.js  # 单个测试
```

### 示例数据

见 `docs/sample-data.json`，含 3 个用户、3 个帖子、2 个成果、2 个邀请码的完整演示数据。

---

## 数据迁移与兼容说明

- 新增字段均设有默认值（如 `profileCompleted` 默认 `false`），旧数据兼容。
- `admin_logs` 集合为新增，不存在时不影响功能（写入失败会被 catch 忽略）。
- 建议升级时在云开发控制台创建缺失集合并建立索引。

---

## 部署步骤

1. 填写 `project.config.json` 的 `appid`。
2. 修改 `miniprogram/utils/config.js` 的 `CLOUD_ENV_ID`。
3. 右键每个云函数 → 「上传并部署：云端安装依赖」。
4. 云开发控制台创建 7 个集合 + 设置安全规则。
5. 设置云函数环境变量（API Key）。
6. 上传代码 → 提交审核 → 发布。

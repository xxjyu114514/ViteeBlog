# 🔭 ViteeBlog — 观测笔记

> 基于 Vue 3 + FastAPI + MySQL 的全栈个人博客系统。

---

## 📌 项目状态

![Vue](https://img.shields.io/badge/Vue-3.5-4fc08d)
![Vite](https://img.shields.io/badge/Vite-8.0-646cff)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1)
![Pinia](https://img.shields.io/badge/Pinia-3.0-ffd859)

> 已完成前后端全功能联调，支持三种启动模式（Production / Lite / Demo）。

---

## ✨ 功能特性

| 模块 | 说明 |
|------|------|
| **沉浸式页面导航** | 首页 → 文章 → 关于 → 留言，滚轮上下环形切换，滑动过渡动画 |
| **文章系统** | Markdown 编辑（Vditor）、发布/撤回/软删除、归档、搜索、分类标签、置顶、审核流 |
| **评论系统** | 多级嵌套树形评论、Markdown 输入、点赞、举报、管理员审核 |
| **频道聊天** | 频道 CRUD、实时消息轮询、2分钟撤回、重新编辑 |
| **社交关注** | 关注/取消关注、粉丝列表、关注列表 |
| **收藏系统** | 收藏/取消收藏、检查状态、收藏列表 |
| **用户系统** | 注册（邮箱验证码）、登录、密码找回、头像上传、资料编辑、账号注销 |
| **角色权限** | 超级管理员 / 管理员 / 普通用户三级权限 |
| **个人主页** | 3D 倾斜追踪卡片、玻璃拟态按钮面板、手动 Hit-Test |
| **设计系统** | 暗色冷色调主题、毛玻璃效果、沉浸式全屏视图 |

---

## 🧱 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5 | 组件化框架 |
| Vue Router | 4.6 | 路由管理 |
| Pinia | 3.0 | 状态管理 |
| Vite | 8.0 | 构建工具 |
| Dart Sass | 1.98 | SCSS 预处理器 |
| Vditor | 3.11 | Markdown 编辑器 |
| markdown-it | 14.1 | Markdown 渲染 |
| highlight.js | 11.11 | 代码高亮 |
| DOMPurify | 3.4 | XSS 防护 |
| @vueuse/core | 14.2 | 实用工具库 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.135 | 异步 HTTP 框架 |
| SQLAlchemy | 2.x | 异步 ORM |
| Alembic | -- | 数据库迁移 |
| Pydantic | 2.x | 数据校验 |
| aiomysql | -- | MySQL 异步驱动 |
| aiosqlite | -- | SQLite 异步驱动 |
| passlib(bcrypt) | -- | 密码哈希 |
| python-jose | -- | JWT 令牌 |
| uvicorn | 0.42 | ASGI 服务器 |

---

## 🚀 快速开始

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py          # 生产模式（MySQL）
python main.py -lite    # Lite 模式（SQLite）
python main.py -demo    # Demo 模式（MySQL + 公网）
```

### 启动前端

```bash
cd frontend
npm install
npm run dev           # 本地开发
npm run dev:demo      # Demo 模式（公网）
```

---

## 🔥 自研组件详解

### 1. 自研 fetch 封装 (api/client.js)

在浏览器原生 fetch() 之上构建的 HTTP 客户端层，替代 Axios 等第三方库。

- Token 自动注入（Authorization: Bearer）
- camelCase / snake_case 自动转换
- 请求超时控制（10s）
- 自动重试（2 次指数退避）
- GET 请求缓存（30s TTL）
- 401 自动登出
- 统一返回格式 { success, data, message }

### 2. 通用 API 调用包装 (composables/useApi.js)

提供 { data, loading, error, execute } 标准格式，消除所有 try-catch-loading 模板代码。
内置 submitLock 防重复提交锁。

### 3. 沉浸式页面过渡动画 (composables/usePageTransition.js)

四页面滚轮导航：首页 → 文章 → 关于 → 留言。
前进 clipPath 展开动画 800ms，后退透明度过渡 800ms。

### 4. 嵌套评论树 (components/CommentList.vue)

后端返回扁平列表，前端 Map 构建嵌套树结构。
点赞/回复/删除均递归更新本地状态。

### 5. 个人中心 3D 倾斜 (views/user/PersonalCenterView.vue)

鼠标追踪 → rotateX/rotateY，requestAnimationFrame 驱动。
pointer-events: none 禁用浏览器检测，AABB 碰撞检测手动触发点击。

### 6. 状态包装器 (components/StateWrapper.vue)

loading / error / empty 三态组件，支持重试回调。

### 7. 数据库多模式架构 (core/database.py)

一套代码通过启动参数切换三种模式：
- python main.py → MySQL (127.0.0.1:8000)
- python main.py -lite → SQLite (127.0.0.1:8000)
- python main.py -demo → MySQL (0.0.0.0:8000)

---

## 📖 文档索引

| 文档 | 说明 |
|------|------|
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | 完整 API 接口文档 |
| [FRONTEND_STATUS.md](./FRONTEND_STATUS.md) | 前端修复状态跟踪 |

---

## 🔗 相关链接

- GitHub: https://github.com/xxjyu114514/ViteeBlog

## 感谢这个项目的所有贡献者！！
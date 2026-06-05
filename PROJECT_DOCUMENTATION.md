# ViteeBlog 项目完整文档

> 冷色调机能风 · 明日方舟美学 · 0 圆角 · 毛玻璃设计系统

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [快速启动](#3-快速启动)
4. [目录结构](#4-目录结构)
5. [路由系统](#5-路由系统)
6. [SCSS 架构与变量系统](#6-scss-架构与变量系统)
7. [图片管理](#7-图片管理)
8. [组件文档](#8-组件文档)
9. [页面文档](#9-页面文档)
10. [个人主页变量配置](#10-个人主页变量配置)
11. [关于详情页配置](#11-关于详情页配置)
12. [后端 API](#12-后端-api)
13. [设计规范](#13-设计规范)

---

## 1. 项目概述

ViteeBlog 是一个专注于技术分享与个人表达的知识平台。设计语言融合**明日方舟冷色美学**与 **GitHub 暗色层次**，采用**零圆角硬边 + 毛玻璃**的独特视觉风格。

### 核心设计理念

- **冷色调机能风** — 冰蓝主色 `#58a6ff`，冷紫辅色 `#6c5ce7`
- **多层灰度体系** — 背景/面板/悬浮层明度至少差 15，确保层次清晰
- **毛玻璃系统** — `backdrop-filter: blur(16px)` + 半透明背景
- **0 圆角** — 所有元素边界尖锐，硬边美学
- **3D 追踪** — 个人主页卡片随鼠标倾斜

---

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | Composition API + `<script setup>` |
| 状态管理 | Pinia | `userStore`, 全局用户状态 |
| 路由 | Vue Router 4 | 懒加载 + 路由守卫 |
| 样式 | SCSS | 模块化设计令牌 + 全局变量 |
| HTTP 客户端 | 自研 fetch 封装 | 自动 camelCase/snake_case 转换 + 请求缓存 + 重试 |
| 后端 | Python FastAPI | 异步 ORM + JWT 认证 |
| 数据库 | PostgreSQL | SQLAlchemy 2.0 async |
| Markdown | markdown-it | 文章渲染 + 内联解析 |

---

## 3. 快速启动

### 前端

```bash
cd frontend
npm install
npm run dev        # 开发服务器 (默认 localhost:5173)
npm run build      # 生产构建
```

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload   # 开发服务器 (默认 localhost:8000)
```

---

## 4. 目录结构

```
ViteeBlog/
├── frontend/
│   └── src/
│       ├── api/                    # HTTP 客户端封装
│       │   └── client.js           # fetch 封装 (camelCase转换/缓存/重试)
│       ├── assets/
│       │   ├── styles/             # 全局 SCSS
│       │   │   ├── _variables.scss # 设计令牌 + 向后兼容别名
│       │   │   ├── _mixins.scss    # 沉浸式视图 mixin
│       │   │   ├── _images.scss    # ★ 图片路径集中管理
│       │   │   └── views.scss      # 全局视图样式
│       │   ├── team/               # 团队成员照片 (photo-1~5.jpg)
│       │   ├── Font/               # 字体文件
│       │   ├── hero-bg.webp        # 全屏背景图
│       │   ├── personl.webp        # 个人主页背景
│       │   └── about-bg.jpg        # 关于页面背景
│       ├── components/             # 公共组件
│       │   ├── Navbar.vue          # ★ 导航栏 (含返回按钮/路由检测)
│       │   ├── PostItem.vue        # 文章卡片
│       │   ├── PostList.vue        # 文章列表
│       │   ├── Comment*.vue        # 评论系统
│       │   └── StateWrapper.vue    # 加载/错误/空状态
│       ├── composables/            # 组合式函数
│       │   └── usePageTransition.js
│       ├── services/               # API 服务层
│       │   └── articleService.js   # 文章相关接口
│       ├── styles/                 # 页面级全局样式
│       │   ├── index.scss          # 暗色主题入口
│       │   └── immersive.scss      # 沉浸式视图样式
│       ├── views/                  # 页面组件
│       │   ├── HomeView.vue        # 首页 (沉浸式)
│       │   ├── PostPage.vue        # 文章列表 (沉浸式+子页面共用)
│       │   ├── ArticleDetailView.vue     # 文章详情
│       │   ├── AboutImmersiveView.vue    # 关于 (沉浸式入口)
│       │   ├── AboutDetailView.vue       # ★ 关于详情 (团队介绍)
│       │   ├── MessageImmersiveView.vue  # 留言 (沉浸式入口)
│       │   ├── MessageView.vue           # 留言聊天室
│       │   ├── PersonalCenterView.vue    # ★ 个人主页 (含变量配置)
│       │   ├── LoginView.vue             # 登录/注册
│       │   ├── SearchView.vue            # 文章搜索
│       │   ├── ArchiveView.vue           # 文章归档
│       │   ├── *_ManageView.vue          # 管理页面
│       │   ├── *_AdminView.vue           # 后台页面
│       │   └── _design/                  # 设计系统展示
│       │       ├── _tokens.scss          # ★ 设计令牌定义
│       │       ├── _components.scss      # Hero按钮/卡片/徽章等
│       │       └── ...
│       ├── stores/
│       │   └── user.js            # Pinia 用户状态
│       └── utils/
│           └── index.js           # 工具函数 (markdown渲染等)
│
└── backend/
    ├── main.py                    # FastAPI 入口
    ├── models/
    │   └── blog_models.py         # 数据模型 (Article/Comment/User...)
    ├── routers/
    │   └── v1/api_article.py      # 文章接口
    └── schemas/                   # Pydantic 数据校验
```

---

## 5. 路由系统

### 完整路由表

| 路径 | 名称 | 页面 | 权限 | 说明 |
|------|------|------|------|------|
| `/` | home | HomeView | 公开 | 首页 |
| `/posts-immersive` | posts-immersive | PostPage | 公开 | 文章页（沉浸式） |
| `/posts` | posts | PostPage | 公开 | 文章列表（子页面） |
| `/article/:id` | article-detail | ArticleDetailView | 公开 | 文章详情 |
| `/about-immersive` | about-immersive | AboutImmersiveView | 公开 | 关于（沉浸入口） |
| `/about` | about | AboutView | 公开 | 关于（子页面） |
| `/about-detail` | about-detail | AboutDetailView | 公开 | ★ 关于详情（团队介绍） |
| `/message-immersive` | message-immersive | MessageImmersiveView | 公开 | 留言（沉浸入口） |
| `/message` | message | MessageView | 公开 | 留言聊天室 |
| `/search` | search | SearchView | 公开 | 文章搜索 |
| `/archive` | archive | ArchiveView | 公开 | 文章归档 |
| `/login` | login | LoginView | 游客 | 登录/注册 |
| `/personal` | personal | PersonalCenterView | 登录 | ★ 个人主页 |
| `/favorites` | favorites | FavoritesView | 登录 | 我的收藏 |
| `/social` | social | SocialView | 登录 | 社交关系 |
| `/edit-article` | article-edit | ArticleEditView | 登录 | 新建文章 |
| `/edit-article/:id` | article-edit-detail | ArticleEditView | 登录 | 编辑文章 |
| `/manage-articles` | — | ArticleManageView | 登录 | 我的文章管理 |
| `/admin-dashboard` | — | AdminDashboardView | 管理员 | 管理中心 |
| `/categories` | — | CategoryManageView | 管理员 | 分类管理 |
| `/tags` | — | TagManageView | 管理员 | 标签管理 |
| `/comment-admin` | — | CommentAdminView | 管理员 | 评论审核 |
| `/comment-reports` | — | CommentReportListView | 管理员 | 举报管理 |
| `/article-import` | — | ArticleImportView | 管理员 | 文章导入 |
| `/admin-import` | — | AdminImportView | 管理员 | 导入管理 |
| `/users/:id` | user-profile | UserProfileView | 公开 | 用户主页 |

### 导航栏返回按钮

定义在 `components/Navbar.vue`，通过路由自动检测是否显示：

```js
// 不需要返回按钮的顶层页面
const mainPages = ['/', '/posts-immersive', '/about-immersive', '/message-immersive', '/personal']
// 其余所有路由自动显示 < 返回按钮
```

---

## 6. SCSS 架构与变量系统

### 文件依赖图

```
_images.scss                    ← 图片路径唯一源头
  └→ _tokens.scss ( @forward )  ← 设计令牌
       └→ _variables.scss ( @use + @forward )  ← 兼容别名层
            └→ 所有 Vue 文件 ( @use '@/assets/styles/variables' as * )

_design.scss                    ← 设计系统入口
  ├→ _tokens.scss
  ├→ _components.scss           ← Hero按钮 / Badge / 卡片 / 表单
  └→ ... (其他组件文件)
```

### 颜色系统

| 角色 | 变量 | 色值 | 用途 |
|------|------|------|------|
| 主色 | `$color-primary` | `#58a6ff` | 按钮/链接/强调 |
| 辅色 | `$color-secondary` | `#6c5ce7` | 冷紫装饰 |
| 强调色 | `$color-accent` | `#00cec9` | 青绿点缀 |
| 成功 | `$color-success` | `#2ea043` | 冷绿 |
| 警告 | `$color-warning` | `#d29922` | 暗黄 |
| 错误 | `$color-error` | `#da3633` | 暗红 |

### 背景层次

| 层级 | 变量 | 色值 | 用途 |
|------|------|------|------|
| 最底层 | `$bg-base` | `#0d1117` | 页面底色 |
| 面板/卡片 | `$bg-surface` | `#1c2128` | 组件容器 |
| 悬浮层 | `$bg-elevated` | `#2d333b` | 输入框/弹窗 |
| Hover | `$bg-hover` | `#3d444d` | 悬停状态 |

### 毛玻璃系统

| 变量 | 值 | 用途 |
|------|------|------|
| `$glass-bg` | `rgba(255,255,255,0.06)` | 毛玻璃底色 |
| `$glass-bg-hover` | `rgba(255,255,255,0.10)` | 悬停加深 |
| `$glass-border` | `rgba(255,255,255,0.10)` | 毛玻璃边框 |
| `$glass-border-hover` | `rgba($color-primary, 0.3)` | 悬停边框 |
| `$glass-blur` | `16px` | 模糊强度 |
| `$glass-blur-heavy` | `24px` | 重模糊 |

### 文字层级

| 层级 | 变量 | 色值 |
|------|------|------|
| 主文字 | `$text-primary` | `#B0B8C5` |
| 次要文字 | `$text-secondary` | `#8b949e` |
| 辅助文字 | `$text-tertiary` | `#6e7681` |
| 禁用文字 | `$text-disabled` | `#484f58` |

### 向后兼容别名（`_variables.scss`）

旧组件可直接使用以下别名，无需修改代码：

| 别名 | 映射 |
|------|------|
| `$bg-dark` | `$bg-base` |
| `$bg-white` | `$bg-surface` |
| `$bg-smoke` | `$bg-hover` |
| `$text-main` | `$text-primary` |
| `$border-color` | 纯色 `rgba(255,255,255,0.15)` |

---

## 7. 图片管理

### 集中管理文件：`frontend/src/assets/styles/_images.scss`

所有图片路径统一在此定义，修改一处全项目生效。

```scss
// --- 全屏背景（每个页面独立变量） ---
$img-home-bg:        '@/assets/hero-bg.webp';   // 首页
$img-posts-bg:       '@/assets/hero-bg.webp';   // 文章列表（沉浸式）
$img-posts-list-bg:  '@/assets/hero-bg.webp';   // 文章列表（子页面）
$img-post-detail-bg: '@/assets/hero-bg.webp';   // 文章详情
$img-about-bg:       '@/assets/about-bg.jpg';   // 关于页面 / 设计系统
$img-message-bg:     '@/assets/hero-bg.webp';   // 留言（子页面）
$img-personal-bg:    '@/assets/personl.webp';   // 个人主页

// --- 团队头像 ---
$img-team-1:  '@/assets/team/photo-1.jpg';   // 北极星
$img-team-2:  '@/assets/team/photo-2.jpg';   // 方舟骑士
$img-team-3:  '@/assets/team/photo-3.jpg';   // 数据游侠
$img-team-4:  '@/assets/team/photo-4.jpg';   // 代码诗人
$img-team-5:  '@/assets/team/photo-5.jpg';   // 观测者

// --- 字体 ---
$font-heavy:  '@/assets/Font/PingFang SC Heavy.ttf';
```

### 使用方式

```scss
// SCSS 中使用
background: $bg-dark url(#{$img-home-bg}) center/cover;

// Vue 模板中使用
background: url(#{$img-personal-bg}) right top / cover fixed;
```

### 添加/更换图片

1. 将图片文件放入 `frontend/src/assets/` 对应目录
2. 修改 `_images.scss` 中对应变量的路径
3. 全项目自动生效

### 团队头像

存放位置：`frontend/src/assets/team/`
文件名：`photo-1.jpg` ~ `photo-5.jpg`

---

## 8. 组件文档

### Navbar.vue — 导航栏

**位置**：`components/Navbar.vue`

**功能**：
- 固定顶部导航栏（90px，毛玻璃效果）
- 4 个主菜单项：首页 / 文章 / 关于 / 留言
- 搜索入口 / 登录按钮 / 个人中心入口
- ★ 智能返回按钮：根据路由自动显示/隐藏

**返回按钮推理**：
```js
// 在这 5 个页面不显示，其余全部显示
const mainPages = ['/', '/posts-immersive', '/about-immersive', '/message-immersive', '/personal']
const showBackBtn = computed(() => !mainPages.includes(route.path))
```

**样式**：毛玻璃固定定位，`height: 90px`，`z-index: 9999`

---

### PostItem.vue — 文章卡片

**功能**：展示单篇文章摘要

**数据字段**：
- `post.publishedAt` — 发布时间
- `post.viewCount` — 阅读量
- `post.title` — 标题（支持 Markdown 内联渲染）
- `post.summary` — 摘要

**注意**：所有字段为 camelCase（API 响应自动转换自 snake_case）

---

### PostList.vue — 文章列表

**功能**：文章列表 + 最新/热门排序

**排序逻辑**：热门按 `viewCount` 降序排列

---

## 9. 页面文档

### 个人主页 — PersonalCenterView.vue

**路由**：`/personal`（需登录）

**布局**：左右两栏，3D 鼠标追踪倾斜

- **左栏**：用户信息卡片（头像/昵称/统计）
- **右栏**：5 个 hero-button 功能入口

**背景**：`$img-personal-bg`（`personl.webp`）右对齐覆盖

**按钮功能**：
| 按钮 | 跳转 | 说明 |
|------|------|------|
| 新建文章 | `/edit-article` | 蓝色渐变 `to top` |
| 已收藏文章 | `/favorites` | 白色渐变 |
| 关注列表 | `/social` | 白色渐变 |
| 管理中心/我的文章 | `/admin-dashboard` 或 `/manage-articles` | 管理员/用户自适应 |
| 设置 | 弹窗 | 方形，渐变朝下，图标在上 |

**弹窗系统**：
- 账户设置 → 上传头像 / 编辑资料 / 修改密码 / 注销账号 / 退出登录
- 编辑资料 → 修改昵称和简介
- 修改密码 → 旧密码 + 新密码验证

**3D 倾斜配置**：
```js
const tiltConfig = {
  maxRotate: 5,        // 最大倾斜角度
  resetDuration: 200,  // 回正动画时长(ms)
  leftDefaultY: 15,    // 左卡片默认右倾
  rightDefaultY: -15,  // 右卡片默认左倾
}
```

**入场/退场动画**：
- 入场：左卡片从 `translateX(-60px)` 滑入，按钮从 `translateX(60px)` 滑入
- 退场：反向滑出 + 淡出

---

### 关于详情 — AboutDetailView.vue

**路由**：`/about-detail`

**结构**：

1. **顶部文章区**（100vh 居中）
   - 大标题 `"关于观测笔记"`
   - Markdown 介绍文章

2. **团队画廊**（5 个矩形卡片）
   - 每人占 20vw × 70vh
   - 左侧人物图片 + 右侧渐变背景
   - 默认亮度 70%，悬停 100%
   - 名字显示在矩形上方

**交互**：点击任一矩形 → 展开至 100vw，隐藏其余 4 个，右侧显示详情面板

**团队成员数据**：
```js
const team = [
  { name: 'xxjyu',   role: '创始人 & 全栈工程师', ... },
  { name: '区',      role: 'UI/UX 设计师',       ... },
  { name: '杨威先生', role: '后端架构师',          ... },
  { name: '91丘先生', role: '后端工作者',          ... },
  { name: '周',      role: '产品经理 & 内容运营',  ... },
]
```

**图片**：本地 `@/assets/team/photo-1.jpg` ~ `photo-5.jpg`

---

### 留言页 — MessageView.vue

**路由**：`/message`

**功能**：实时聊天频道
- 左侧频道列表（管理员可创建/编辑/删除频道）
- 右侧聊天区（发送消息/撤回/重新编辑）
- 5 秒轮询新消息

**样式**：全页毛玻璃卡片（`rgba(45, 51, 59, 0.82)` + `blur(16px)`），背景使用 `$img-message-bg`

---

### 文章列表 — PostPage.vue / PostListView.vue

**PostPage.vue**：沉浸式入口 + 子页面共用（`/posts-immersive` 和 `/posts` 使用同一组件）

**PostListView.vue**：纯列表视图

**背景**：
- 沉浸式：`$img-posts-bg`
- 子页面：`$img-posts-list-bg`
- 详情：`$img-post-detail-bg`

---

## 10. 个人主页变量配置

位置：`PersonalCenterView.vue` 的 `<style>` 顶部（第 609 行）

### 按钮面板

```scss
$panel-max-height: 80vh;        // 面板最大高度
$panel-gap:        $space-md;   // 按钮行间距
```

### 每个按钮独立配置

```scss
// 新建文章
$btn-new:      ( w:22vh, h:14vh, offset:5vw, dir:to right, icon:'✏️', label:'新建文章',   sub:'NEW_POST' );
// 已收藏文章
$btn-fav:      ( w:22vh, h:14vh, offset:5vw, dir:to right, icon:'⭐',  label:'已收藏文章', sub:'FAVORITES' );
// 关注列表
$btn-social:   ( w:22vh, h:14vh, offset:5vw, dir:to right, icon:'👥',  label:'关注列表',   sub:'SOCIAL' );
// 管理中心
$btn-manage:   ( w:24vh, h:17vh, dir:to right, icon:'📂', label:'管理中心', label2:'我的文章', sub:'ADMIN' );
// 账户设置
$btn-account:  ( w:10vh, h:14vh, dir:to bottom, icon:'⚙️', label:'设置' );
```

**修改方式**：直接改 map 中的 `w`/`h`/`icon`/`label`，该按钮独立生效。

### 白色渐变断点

```scss
$gradient-fade-in: 65%;
$gradient-peak:    78%;
$gradient-opacity: (fade:0.04, mid:0.08, strong:0.10, peak:0.15);
```

---

## 11. 关于详情页配置

位置：`AboutDetailView.vue`

### 画廊配置

| 属性 | 值 | 说明 |
|------|-----|------|
| 矩形高度 | `70vh` | 在 `getItemStyle()` 中定义 |
| 折叠宽度 | `20vw` | 5 列均分 |
| 展开宽度 | `100vw` | 全屏 |
| 展开速度 | `0.6s cubic-bezier(0.65,0,0.35,1)` | |
| 图片默认亮度 | `0.7` | 70% |
| 图片悬停亮度 | `1.0` | 100% |
| 名字位置 | 矩形上方 | flex column 布局 |
| 名字字体 | `1.6rem`, `800` | 白色 `#fff` |

### 渐变背景

```scss
linear-gradient(to top,
  #[纯色] 0%,         // 底部 80% 纯色
  #[纯色] 80%,
  transparent 100%     // 顶部 20% 渐变到透明
)
```

每人纯色不同：`#0f0c29` / `#1a1a2e` / `#0d1117` / `#1b1b2f` / `#0a0a23`

---

## 12. 后端 API

### 文章接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/article/public/list` | 公开文章列表（含 `view_count` + `like_count` + `comment_count`） |
| GET | `/article/{id}` | 文章详情（含 `like_count` + `is_liked`） |
| POST | `/article/{id}/like` | 点赞/取消点赞 |
| GET | `/article/{id}/like/count` | 查看点赞数 |
| GET | `/article/public/search` | 搜索文章 |
| GET | `/article/public/archive` | 文章归档 |

### 数据模型关键字段

**Article**：
- `view_count`（DB 列）— 阅读量，每次请求详情自动 +1
- `like_count`（运行时属性）— 点赞数，接口调用时实时查询
- `comment_count`（运行时属性）— 评论数，排除已删除

### API 响应自动 camelCase 转换

前端 `client.js` 自动将后端返回的 `snake_case` 转为 `camelCase`：
- `view_count` → `viewCount`
- `like_count` → `likeCount`
- `comment_count` → `commentCount`
- `published_at` → `publishedAt`

---

## 13. 设计规范

### 间距系统（8px 基准）

| 名称 | 值 | 用途 |
|------|------|------|
| `$space-2xs` | 4px | 极紧凑 |
| `$space-xs` | 8px | 图标旁距 |
| `$space-sm` | 12px | 组件内距 |
| `$space-md` | 16px | 间距 |
| `$space-lg` | 24px | 卡片内距 |
| `$space-xl` | 32px | 区块间距 |
| `$space-2xl` | 48px | 大区块 |
| `$space-3xl` | 64px | 页面间距 |

### 过渡时间

| 变量 | 值 | 用途 |
|------|------|------|
| `$transition-fast` | `0.15s ease` | 微交互 |
| `$transition-base` | `0.25s ease` | 常规过渡 |
| `$transition-slow` | `0.4s ease` | 大范围动画 |

### 字体

| 变量 | 值 | 用途 |
|------|------|------|
| `$font-mono` | `'SF Mono', 'JetBrains Mono', ...` | 标题/代码/数据 |
| `$font-sans` | `-apple-system, ..., 'Noto Sans SC'` | 正文/UI |

### 发光效果

```scss
$glow-sm:   0 0 0 1px rgba(255,255,255,0.06);
$glow-md:   0 0 0 1px rgba(255,255,255,0.10), 0 4px 20px rgba(0,0,0,0.5);
$glow-lg:   0 0 0 1px rgba(255,255,255,0.15), 0 8px 32px rgba(0,0,0,0.6);
$glow-brand: 0 0 0 1px rgba($color-primary,0.3), 0 0 20px rgba($color-primary,0.1);
```

### CSS 编写规范

1. **变量优先**：颜色/间距/过渡使用 SCSS 变量，禁止硬编码色值
2. **图片集中**：所有 `url()` 使用 `_images.scss` 变量
3. **模块化**：按功能拆分 SCSS 文件，通过 `@use`/`@forward` 组织
4. **命名一致性**：BEM 风格，`组件名__元素--修饰符`
5. **0 圆角**：不使用 `border-radius`，保持硬边风格

---

> 文档最后更新：2026-06-05

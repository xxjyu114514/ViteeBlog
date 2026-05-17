# ViteeBlog 项目技术文档（AI专用）

## 1. 项目概述

**ViteeBlog** 是一个现代化的前后端分离博客系统，专为个人内容创作和管理设计。项目采用 **Vue 3 + FastAPI** 技术栈，支持完整的文章生命周期管理、用户权限控制和内容审核流程。

### 核心价值
- **轻量级部署**: 支持 SQLite 轻量化模式，降低开发和部署门槛
- **完整工作流**: 提供从草稿 → 审核 → 发布的完整内容管理流程
- **安全机制**: 包含登录锁定、防灌水、JWT 认证等多重安全保护
- **沉浸式体验**: 前端提供独特的双模式页面设计（沉浸式/常规）

## 2. 系统架构

### 2.1 整体架构
```
ViteeBlog (前后端分离)
├── Frontend: Vue 3 SPA (单页应用)
└── Backend: FastAPI RESTful API
```

### 2.2 前后端交互
- **Base URL**: `http://127.0.0.1:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **Content-Type**: `application/json`
- **静态资源**: `/storage` 路径提供文件服务

### 2.3 数据存储策略
- **数据库**: MySQL (生产) / SQLite (开发)
- **文章内容**: Markdown 文件存储 (`storage/articles/`)
- **图片资源**: 文件系统存储 (`storage/images/`)
- **元数据**: 数据库存储 (标题、状态、分类、标签等)

## 3. 技术栈详情

### 3.1 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.30 | 核心框架 |
| Vite | 8.0.1 | 构建工具 |
| Vue Router | 4.6.4 | 路由管理 |
| Pinia | 3.0.4 | 状态管理 |
| Sass | 1.98.0 | CSS 预处理器 |
| Vditor | - | Markdown 编辑器 |

### 3.2 后端技术栈
| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| SQLAlchemy | ORM |
| Alembic | 数据库迁移 |
| Pydantic | 数据验证 |
| aiomysql | 异步 MySQL 驱动 |
| JWT | 身份认证 |
| aiosqlite | 异步 SQLite 驱动 |

### 3.3 开发环境要求
- **Python**: 3.7+
- **Node.js**: 16+ (LTS 推荐)
- **数据库**: MySQL 5.7+ 或 SQLite 3.8.3+

## 4. 核心功能模块

### 4.1 用户认证系统
- **注册流程**: 邮箱验证码两步验证
- **登录机制**: JWT Token (60分钟有效期)
- **安全保护**: 连续3次失败锁定15分钟
- **角色管理**: `common` (普通用户) / `admin` (管理员)

### 4.2 文章管理系统
#### 状态流转
```
DRAFT → PENDING → PUBLISHED
   ↑        ↓
   └───── REJECTED
```

#### 核心功能
- **自动保存**: 防抖实时保存草稿
- **审核流程**: 普通用户提交 → 管理员审核
- **回收站**: 软删除 + 恢复功能
- **硬删除**: 永久删除（不可逆）
- **图片上传**: 支持 JPG/PNG/GIF/WebP (≤10MB)

### 4.3 元数据管理
- **分类管理**: 管理员专属创建/删除
- **标签管理**: 用户可创建，管理员可删除
- **防重复**: 标签名称去重处理

### 4.4 评论与互动
- **嵌套回复**: 支持多层评论
- **举报机制**: 用户可举报不当评论
- **管理员审核**: 评论巡查和处理

## 5. 前端架构特色

### 5.1 双模式页面设计
| 模式 | 路径示例 | 特点 |
|------|----------|------|
| 沉浸式 | `/`, `/posts-immersive` | 透明导航栏、毛玻璃效果 |
| 常规 | `/posts`, `/about` | 白色背景、标准布局 |

### 5.2 页面过渡动画
- **前进动画**: 新页面右侧切入
- **后退动画**: 新页面左侧淡入
- **路由索引**: 通过 `meta.index` 控制层级

### 5.3 滚轮导航系统
- **支持页面**: 首页 → 文章 → 关于 → 留言
- **向上滚动**: 返回上一页
- **向下滚动**: 进入下一页

### 5.4 路由守卫
- **requiresAuth**: 需要登录
- **guestOnly**: 仅限游客（如登录页）
- **requiresAdmin**: 需要管理员权限

## 6. API 接口规范

### 6.1 认证相关
- `POST /auth/send-register-code`: 发送注册验证码
- `POST /auth/register`: 用户注册
- `POST /auth/login`: 用户登录

### 6.2 文章相关
- `POST /article/autosave`: 自动保存文章
- `GET /article/{id}`: 获取文章详情
- `PUT /article/{id}/publish`: 提交审核/发布
- `POST /article/upload-image`: 上传图片

### 6.3 元数据相关
- `GET /meta/categories`: 获取所有分类
- `POST /meta/categories`: 创建分类 (管理员)
- `GET /meta/tags`: 获取所有标签

### 6.4 管理员专属
- `GET /article/admin/pending`: 获取待审核文章
- `POST /article/admin/articles/{id}/review`: 审核文章

## 7. 开发与部署指南

### 7.1 快速启动
```bash
# 后端 (Lite模式 - SQLite)
cd backend
pip install -r requirements.txt
python main.py -lite

# 前端
cd frontend  
npm install
npm run dev
```

### 7.2 数据库迁移
```bash
# 在 backend/ 目录下执行
alembic revision --autogenerate -m "描述修改"
alembic upgrade head
```

### 7.3 环境配置
- **.env 文件**: 配置数据库连接、JWT密钥、邮件服务等
- **Lite模式**: 无需配置数据库，自动使用SQLite

### 7.4 构建生产版本
```bash
# 前端构建
cd frontend
npm run build

# 后端生产部署
# 配置 .env 文件中的 MySQL 连接信息
python main.py
```

## 8. 项目目录结构

### 8.1 后端目录结构
```
backend/
├── alembic/              # 数据库迁移
├── core/                 # 核心配置
│   ├── config.py         # 环境配置
│   ├── database.py       # 数据库连接
│   ├── security.py       # 安全工具
│   └── mail.py           # 邮件服务
├── models/               # 数据模型
├── repository/           # 数据访问层
├── routers/v1/           # API路由
├── schemas/              # 数据验证模型
├── storage/              # 静态文件存储
└── main.py               # 应用入口
```

### 8.2 前端目录结构
```
frontend/
├── src/
│   ├── assets/           # 静态资源
│   ├── components/       # 可复用组件
│   ├── composables/      # 组合式函数
│   ├── router/           # 路由配置
│   ├── stores/           # 状态管理
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── public/vditor/        # Markdown编辑器
└── vite.config.js        # 构建配置
```

## 9. 安全与性能考虑

### 9.1 安全机制
- **输入验证**: Pydantic 严格验证所有请求数据
- **权限控制**: RBAC (基于角色的访问控制)
- **防暴力破解**: 登录失败锁定机制
- **防灌水**: 普通用户最多3篇待审核文章
- **XSS防护**: Markdown 内容自动转义

### 9.2 性能优化
- **异步处理**: FastAPI 异步非阻塞架构
- **连接池**: MySQL 连接池配置 (pool_size=10)
- **代码分割**: 前端路由懒加载
- **硬件加速**: CSS transform 动画优化

## 10. 扩展与定制

### 10.1 可扩展点
- **邮件服务**: 可替换为其他邮件提供商
- **存储策略**: 可扩展至云存储 (AWS S3, 阿里云OSS)
- **认证方式**: 可集成 OAuth2、微信登录等
- **搜索引擎**: 可集成 Elasticsearch 全文搜索

### 10.2 自定义配置
- **主题定制**: 修改 SCSS 变量文件
- **API前缀**: 修改路由前缀配置
- **Token有效期**: 调整 `.env` 中的过期时间
- **文件大小限制**: 修改上传接口的验证逻辑

## 11. 常见问题与解决方案

### 11.1 数据库相关
- **Q**: 提示 "Target database is not up to date"
  **A**: 执行 `alembic upgrade head`

- **Q**: 迁移文件未检测到模型变化
  **A**: 确保 `alembic/env.py` 正确导入所有模型

### 11.2 开发环境
- **Q**: 前端无法连接后端API
  **A**: 检查 CORS 配置和端口是否正确

- **Q**: Lite模式启动失败
  **A**: 确保在 `backend/` 目录下执行命令

### 11.3 权限问题
- **Q**: 普通用户无法访问管理功能
  **A**: 这是正常的安全机制，需要管理员权限

## 12. 贡献指南

### 12.1 代码规范
- **Python**: 遵循 PEP 8 规范
- **TypeScript/JavaScript**: 使用 ESLint + Prettier
- **SCSS**: 遵循 BEM 命名规范

### 12.2 提交流程
1. 创建特性分支
2. 实现功能并添加测试
3. 更新相关文档
4. 提交 Pull Request

### 12.3 测试要求
- **后端**: 添加 Pytest 单元测试
- **前端**: 确保组件功能正常
- **集成**: 验证前后端交互

---

**文档版本**: v1.0  
**最后更新**: 2026-05-04  
**适用对象**: AI助手、开发者、技术团队
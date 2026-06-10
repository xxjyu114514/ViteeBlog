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
- **角色管理**: 
  - `common` (普通用户): 基本功能，可发布文章、评论
  - `admin` (普通管理员): 可审核文章、管理分类/标签、处理举报
  - `super_admin` (超级管理员): 拥有所有管理员权限 + 用户角色管理

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

### 6.4 管理员专属接口

#### 日常管理接口（ADMIN 和 SUPER_ADMIN 均可使用）
- `GET /article/admin/pending`: 获取待审核文章列表
- `POST /article/admin/articles/{id}/review`: 审核文章（通过/驳回）
- `POST /meta/categories`: 创建分类
- `DELETE /meta/categories/{id}`: 删除分类
- `DELETE /meta/tags/{id}`: 删除标签
- `GET /comment/admin/pending`: 获取待审核评论
- `POST /comment/admin/comments/{id}/review`: 审核评论

#### 用户角色管理接口（ADMIN 和 SUPER_ADMIN 均可使用）
- `PUT /auth/admin/users/{user_id}/role`: 修改用户角色（升级/降级）

**重要说明**：
- 普通管理员和超级管理员都可以修改用户角色
- **不能**将任何人升级为超级管理员（只能通过数据库手动设置）
- **不能**修改超级管理员的角色（即使是超管也不行）
- 可以将普通用户升级为普通管理员
- 可以将管理员降级为普通用户
- 不能修改自己的角色
- 全站必须至少保留一名普通管理员

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

## 12. 超级管理员功能详解

### 12.1 角色体系设计

ViteeBlog 采用三级权限体系，确保系统安全性和管理灵活性：

| 角色 | 代码 | 权限范围 |
|------|------|----------|
| 普通用户 | `common` | 发布文章、评论、点赞、收藏等基本功能 |
| 普通管理员 | `admin` | 审核文章/评论、管理分类标签、处理举报、**修改用户角色** |
| 超级管理员 | `super_admin` | 所有管理员权限（但**不能**通过接口创建其他超管） |

### 12.2 权限分级原则

#### 设计理念
- **最小权限原则**: 普通管理员拥有必要的日常管理权限
- **职责分离**: 敏感操作（升级为超管）仅限数据库手动设置
- **防误操作**: 防止管理员之间互相降级导致的管理混乱
- **安全保护**: 超级管理员角色不能被修改

#### 权限继承
```
SUPER_ADMIN
  └── 继承 ADMIN 的所有权限
        ├── 审核文章/评论
        ├── 管理分类/标签
        ├── 处理举报
        └── 修改用户角色（但不能升级为超管）
```

### 12.3 用户角色管理接口

#### 接口详情
```http
PUT /api/v1/auth/admin/users/{user_id}/role
Authorization: Bearer {admin_token 或 super_admin_token}
Content-Type: application/json

{
  "new_role": "admin"  // 可选值: "common", "admin"
}
```

#### 请求参数
- **user_id** (路径参数): 目标用户的 ID
- **new_role** (请求体): 新的角色值
  - `"common"`: 普通用户
  - `"admin"`: 普通管理员
  - ❌ **不能**使用 `"super_admin"`（会返回错误）

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "message": "成功将用户 BaoZi 从 common 变更为 admin"
}
```

**失败响应**:
```json
// 403 Forbidden - 不能升级为超级管理员
{
  "detail": "无法通过接口升级为超级管理员，请联系系统管理员手动设置"
}

// 403 Forbidden - 不能修改超级管理员
{
  "detail": "无法修改超级管理员的角色"
}

// 400 Bad Request - 不能修改自己的角色
{
  "detail": "不能修改自己的角色"
}

// 400 Bad Request - 必须保留至少一名管理员
{
  "detail": "全站必须至少保留一名普通管理员"
}
```

### 12.4 安全校验规则

系统在修改用户角色时会执行以下安全检查：

1. **身份验证**: 必须是管理员（ADMIN 或 SUPER_ADMIN）
2. **自我保护**: 不能修改自己的角色
3. **超管保护**: 不能修改超级管理员的角色
4. **禁止升级超管**: 不能将任何人升级为超级管理员
5. **管理员保留**: 降级最后一个普通管理员时会阻止
6. **用户存在**: 目标用户必须存在

### 12.5 典型使用场景

#### 场晦1：提升新用户为管理员
```bash
# 管理员登录获取 token
POST /api/v1/auth/login
{
  "username": "BaoZi",
  "password": "123456"
}

# 提升用户 ID=2 为管理员
PUT /api/v1/auth/admin/users/2/role
Authorization: Bearer {admin_token}
{
  "new_role": "admin"
}
```

#### 场晦2：降级违规管理员
```bash
# 将违规的管理员降级为普通用户
PUT /api/v1/auth/admin/users/3/role
Authorization: Bearer {admin_token}
{
  "new_role": "common"
}
```

#### 场晦3：手动设置超级管理员（数据库操作）
```sql
-- 只能通过数据库手动设置超级管理员
UPDATE user SET role = 'SUPER_ADMIN' WHERE id = 1;
```

### 12.6 测试用例

项目提供了完整的 HTTP 测试文件：`backend/test_super_admin.http`

#### 测试覆盖
1. ✅ 超管降级管理员 → 应该成功
2. ✅ 超管升级普通用户 → 应该成功
3. ✅ 管理员降级其他管理员 → 应该成功
4. ❌ 尝试升级为超管 → 应该失败 (403)
5. ❌ 尝试修改超管角色 → 应该失败 (403)
6. ❌ 修改自己角色 → 应该失败 (400)
7. ✅ 管理员调用日常管理接口 → 应该成功
8. ✅ 超管调用日常管理接口 → 应该成功

#### 执行测试
```bash
# 1. 启动后端服务器
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 2. 在 VS Code 中打开 test_super_admin.http
# 3. 按顺序执行登录和测试请求
```

### 12.7 数据库迁移

超级管理员功能需要数据库支持 `SUPER_ADMIN` 枚举值。

#### 迁移步骤
```bash
cd backend

# 生成迁移脚本
python -m alembic revision --autogenerate -m "add_super_admin_role"

# 应用迁移
python -m alembic upgrade head

# 验证迁移
python -m alembic current
```

#### 手动设置超级管理员
如果数据库中还没有超级管理员，可以直接修改：

```sql
-- 查看当前管理员
SELECT id, username, email, role FROM user WHERE role IN ('ADMIN', 'SUPER_ADMIN');

-- 提升用户为超级管理员
UPDATE user SET role = 'SUPER_ADMIN' WHERE id = 1;
```

### 12.8 最佳实践

#### 建议
1. **至少两个超级管理员**: 防止单点故障
2. **谨慎授予 SUPER_ADMIN**: 仅信任的核心人员
3. **定期审计**: 检查管理员权限分配情况
4. **日志监控**: 关注角色变更操作日志
5. **备份策略**: 变更前备份数据库

#### 避免
1. ❌ 不要将所有管理员都设为 SUPER_ADMIN
2. ❌ 不要在未确认的情况下修改角色
3. ❌ 不要删除最后一个普通管理员
4. ❌ 不要在生产环境直接执行 SQL 修改

### 12.9 故障排查

#### 问题1：提示“无法通过接口升级为超级管理员”
**原因**: 尝试通过 API 设置为 SUPER_ADMIN  
**解决**: 只能通过数据库手动设置

```sql
UPDATE user SET role = 'SUPER_ADMIN' WHERE id = 你的ID;
```

#### 问题2：提示“无法修改超级管理员的角色”
**原因**: 目标用户是 SUPER_ADMIN（受保护）  
**解决**: 超级管理员角色不能被修改，即使是超管也不行

#### 问题3：提示“不能修改自己的角色”
**原因**: 尝试修改自己的角色（安全机制）  
**解决**: 这是正常行为，需要另一个管理员来修改

#### 问题4：提示“全站必须至少保留一名普通管理员”
**原因**: 降级操作会导致没有普通管理员  
**解决**: 先创建或提升一个新的普通管理员

---

## 13. 贡献指南

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

**文档版本**: v2.1  
**最后更新**: 2026-06-11  
**主要更新**: 修正用户角色管理权限说明 - 普通管理员也可修改角色  
**适用对象**: AI助手、开发者、技术团队
# ViteeBlog 项目开发手册

本仓库采用前后端分离架构。`frontend/` 为 Vue3 前端项目，`backend/` 为 FastAPI 后端项目。

## 🚀 快速开始

### 后端服务
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 接口文档
服务启动后访问：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📋 通用规范

### 基础信息
- **Base URL**: `http://127.0.0.1:8000/api/v1`
- **Content-Type**: `application/json`
- **鉴权方式**: JWT Token（登录成功后获取）

### 请求头示例
```
Authorization: Bearer <Your_Token>
```

### 常见状态码
| 状态码 | 含义 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应数据 |
| 201 | 创建成功 | 资源已成功创建 |
| 400 | 请求错误 | 检查参数格式或业务逻辑 |
| 401 | 未授权 | Token 无效或过期，重新登录 |
| 403 | 禁止访问 | 权限不足（如普通用户尝试管理员操作） |
| 404 | 资源不存在 | 检查 ID 是否正确 |
| 422 | 参数验证失败 | 查看具体字段错误信息 |
| 429 | 请求过于频繁 | 等待指定时间后重试 |
| 500 | 服务器错误 | 联系后端开发或稍后重试 |

---

## 🔐 用户认证模块

### 核心流程
**注册采用两步验证机制：**
1. 调用 `/auth/send-register-code` 获取邮箱验证码
2. 调用 `/auth/register` 携带验证码完成注册

> ⚠️ 验证码一次性有效，校验后立即销毁

### 1. 发送注册验证码

**接口**: `POST /auth/send-register-code`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**成功响应** (200):
```json
{
  "message": "验证码已发送至您的邮箱"
}
```

**错误响应**:
- `400`: 邮箱已被注册
- `429`: 发送过于频繁（60秒内只能发送一次）

**前端注意**:
- ✅ 点击后立即禁用按钮，开启60秒倒计时
- ✅ 只有未注册的邮箱才能发送验证码
- ✅ 验证码有效期10分钟

---

### 2. 用户注册

**接口**: `POST /auth/register`

**请求体**:
```json
{
  "user_in": {
    "username": "BaoZi",
    "email": "user@example.com",
    "password": "123456"
  },
  "email_code": "123456"
}
```

**参数约束**:
- `username`: 3-50个字符
- `password`: 6-128个字符
- `email_code`: 6位数字

**成功响应** (201):
```json
{
  "id": 1,
  "username": "BaoZi",
  "email": "user@example.com",
  "role": "common",
  "created_at": "2026-04-15T20:00:00"
}
```

**错误响应**:
- `400`: 验证码错误或已失效 / 用户名或邮箱已存在
- `422`: 参数验证失败（查看具体字段错误）

---

### 3. 用户登录

**接口**: `POST /auth/login`

**请求体**:
```json
{
  "username": "BaoZi",
  "password": "123456"
}
```

**成功响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "BaoZi",
    "email": "user@example.com",
    "role": "common",
    "created_at": "2026-04-15T20:00:00"
  }
}
```

**错误响应**:
- `401`: 用户名或密码错误 / 账号被锁定
- `403`: 账号锁定中（显示剩余时间）

**⚠️ 安全机制**:
- 连续3次登录失败将锁定账号15分钟
- 登录成功后自动清空失败计数

---

### Token 使用示例

```javascript
// Axios 全局配置
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// 或针对特定请求
axios.get('/api/v1/article/list/public', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

**Token 有效期**: 60分钟（可在 `.env` 中配置）

### 用户角色

| 角色 | 值 | 权限 |
|------|-----|------|
| 普通用户 | `common` | 浏览、评论、留言 |
| 管理员 | `admin` | 文章管理、评论审核等全部权限 |

---


## 轻量化开发模式 (Lite Mode)

为了方便前端调试或快速部署，本项目支持 **SQLite 兼容模式**。在该模式下，你无需安装和配置 MySQL 数据库即可启动完整后端服务。

### 使用方法

在启动项目时，添加 `-lite` 额外参数：

```bash
python main.py -lite


## 🗄️ 数据库迁移（Alembic）

> ⚠️ **重要**：所有 Alembic 命令必须在 `backend/` 目录下执行

### 常用命令

#### 1. 生成迁移文件
```bash
cd backend
alembic revision --autogenerate -m "描述你的修改"
```
**说明**：自动检测模型变化并生成迁移脚本

**示例**：
```bash
alembic revision --autogenerate -m "add published_at to article"
```

#### 2. 应用迁移（升级到最新版本）
```bash
alembic upgrade head
```
**说明**：执行所有未应用的迁移，同步数据库结构

#### 3. 回退迁移
```bash
# 回退一个版本
alembic downgrade -1

# 回退到指定版本
alembic downgrade <revision_id>

# 回退到初始状态（清空所有表）
alembic downgrade base
```

#### 4. 查看迁移历史
```bash
# 查看所有迁移记录
alembic history

# 查看当前数据库版本
alembic current
```

#### 5. 显示待应用的迁移
```bash
alembic heads
```

### 完整工作流程

```bash
# Step 1: 修改 SQLAlchemy 模型（如添加字段）
# 编辑 backend/models/blog_models.py

# Step 2: 生成迁移文件
cd backend
alembic revision --autogenerate -m "add new_field to user"

# Step 3: 检查生成的迁移文件（可选但推荐）
# 查看 backend/alembic/versions/xxx_xxx.py

# Step 4: 应用迁移
alembic upgrade head

# Step 5: 验证数据库已更新
# 连接数据库检查表结构
```

### 常见问题

#### Q1: 提示 "Target database is not up to date"
```bash
# 解决方案：应用所有待执行的迁移
alembic upgrade head
```

#### Q2: 迁移文件生成但没有检测到变化
```bash
# 原因：可能缺少 __tablename__ 或模型未导入
# 解决：确保 alembic/env.py 中正确导入了所有模型

# 在 env.py 中添加：
from models.blog_models import Base
target_metadata = Base.metadata
```

#### Q3: 想重新生成迁移文件
```bash
# 删除最近生成的迁移文件
rm backend/alembic/versions/xxx_xxx.py  # Windows: del backend\alembic\versions\xxx_xxx.py

# 重新生成
alembic revision --autogenerate -m "新的描述"
```

#### Q4: 生产环境如何迁移
```bash
# 生产环境建议先备份数据库
# 然后执行
alembic upgrade head

# 如需回滚
alembic downgrade -1
```

### ⚠️ 注意事项

1. **始终在测试环境先验证迁移**
2. **不要手动修改已应用的迁移文件**
3. **迁移文件一旦提交到版本控制，不要修改**
4. **对于复杂的数据迁移，建议手动编写迁移脚本**
5. **生产环境迁移前务必备份数据库**

### 手动编写迁移示例

```python
# backend/alembic/versions/xxx_add_custom_field.py
"""add custom_field to user"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 添加新字段
    op.add_column('user', 
        sa.Column('custom_field', sa.String(100), nullable=True)
    )
    
    # 为已有数据设置默认值
    op.execute("UPDATE user SET custom_field = 'default' WHERE custom_field IS NULL")

def downgrade():
    # 删除字段
    op.drop_column('user', 'custom_field')
```

---

**最后更新时间**: 2026-04-19  
**文档版本**: v3.1  
**维护者**: Backend Team

---

## 📝 文章管理模块

### 权限说明
- **公开接口**：获取文章列表、获取文章详情、查看分类/标签
- **登录用户**：创建/编辑文章、上传图片、创建标签、提交审核
- **管理员专属**：审核文章、查看全站文章、调整用户权限、管理分类/标签

### 核心功能概览
- ✍️ **自动保存**：实时同步草稿到服务器（文件 + 数据库）
- 📝 **审核流程**：普通用户提交 → 管理员审核 → 发布/驳回
- 🔙 **撤回功能**：可撤回待审核文章重新编辑
- 🛡️ **防灌水**：普通用户最多3篇待审核文章
- 🗑️ **回收站机制**：软删除后数据保留
- ♻️ **恢复功能**：可从回收站恢复误删文章
- 💥 **硬删除**：永久粉碎文章及物理文件

### 文章状态流转

```
草稿 (DRAFT) → 提交审核 → 待审核 (PENDING) → 管理员审核
                                              ↓
                                    ┌─────────┴─────────┐
                                    ↓                   ↓
                              通过 (PUBLISHED)    驳回 (DRAFT)
                                    ↑                   ↓
                                    └───────────────────┘
                                         可重新提交
```

**状态说明**：
- `draft`: 草稿状态，可自由编辑
- `pending`: 待审核状态，禁止编辑（需先撤回）
- `published`: 已发布，公开可见

---

### 1. 自动保存/更新文章

**接口**: `POST /article/autosave`  
**权限**: 所有登录用户

**请求体**:
```json
{
  "id": null,
  "title": "文章标题",
  "summary": "文章摘要",
  "content": "# Markdown 内容\n\n这是文章内容...",
  "category_id": 1,
  "tag_ids": [1, 2]
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | ❌ | 新建时为 null，更新时必填 |
| title | string | ❌ | 文章标题（1-200字符），可选 |
| summary | string | ❌ | 文章摘要（最多500字符） |
| content | string | ❌ | 文章内容（Markdown格式），后端自动保存为文件 |
| content_path | string | ❌ | 可选，如果提供则直接使用，否则根据 content 自动生成 |
| category_id | int | ❌ | 分类ID，可选 |
| tag_ids | int[] | ❌ | 标签ID数组 |

**成功响应** (200):
```json
{
  "id": 1,
  "title": "文章标题",
  "summary": "文章摘要",
  "content_path": "storage/articles/a1b2c3d4.md",
  "category_id": 1,
  "user_id": 1,
  "status": "draft",
  "created_at": "2026-04-26T10:00:00",
  "updated_at": "2026-04-26T10:00:00"
}
```

**错误响应**:
- `400`: 分类不存在
- `403`: 无权操作此文章
- `404`: 文章不存在

**前端注意**:
- ✅ 建议实现防抖保存（停止输入后2秒自动调用）
- ✅ 新建文章返回完整 Article 对象，使用 `response.body.id` 获取文章ID
- ✅ 后端会自动将 `content` 保存为 Markdown 文件并生成 `content_path`
- ⚠️ **待审核状态（PENDING）下禁止编辑**，必须先撤回为草稿
- ⚠️ 保存草稿不会改变文章状态，状态由发布接口控制

---

### 2. 获取文章详情

**接口**: `GET /article/{article_id}`  
**权限**: 公开（已发布文章）/ 作者或管理员（所有状态）

**成功响应** (200):
```json
{
  "id": 1,
  "title": "文章标题",
  "summary": "摘要内容...",
  "content_path": "storage/articles/a1b2c3d4.md",
  "status": "published",
  "submitted_at": null,
  "reviewed_at": null,
  "published_at": "2026-04-25T10:00:00",
  "created_at": "2026-04-25T09:00:00",
  "updated_at": "2026-04-25T10:00:00",
  "deleted_at": null,
  "user_id": 1,
  "category_id": 1,
  "category": { 
    "id": 1, 
    "name": "技术分享" 
  },
  "tags": [
    { "id": 1, "name": "FastAPI" }
  ]
}
```

**权限说明**:
- ✅ **已发布文章**：所有人可查看
- ✅ **草稿/待审核文章**：仅作者和管理员可查看
- ✅ **已删除文章**：仅作者和管理员可查看
- ❌ **未登录用户访问非公开文章**：返回 401
- ❌ **非作者访问他人非公开文章**：返回 403

**前端注意**:
- ✅ 返回 Article 对象，包含分类、标签等关联信息
- ⚠️ **不包含文章内容**，需要通过 `content_path` 单独读取文件
- ⚠️ 根据文章状态和用户身份进行权限判断
- ⚠️ 已删除文章对普通用户不可见

---

### 3. 提交审核/发布文章

**接口**: `PUT /article/{article_id}/publish`  
**权限**: 文章作者或管理员

**功能**: 
- **管理员**: 直接发布文章（跳过审核）
- **普通用户**: 提交文章进入待审核队列

**前置校验**:
1. ✅ 标题不能为空
2. ✅ 文章内容文件必须存在
3. ✅ 文章内容不能为空

**成功响应** (200) - 管理员:
```json
{ "message": "发布成功" }
```

**成功响应** (200) - 普通用户:
```json
{ "message": "已提交审核" }
```

**错误响应**:
- `400`: 发布失败：标题不能为空 / 文章内容文件不存在 / 文章内容不能为空
- `403`: 文章不存在或无权操作

**状态流转**:
- 管理员: `任何状态` → `PUBLISHED`
- 普通用户: `DRAFT/驳回` → `PENDING`

**前端注意**:
- ⚠️ 发布前确保标题和内容不为空
- ⚠️ 确保 autosave 已成功保存内容文件
- ✅ 建议在提交前提示用户确认

---

### 4. 撤回审核中的文章

**接口**: `POST /article/{article_id}/withdraw`  
**权限**: 文章作者

**功能**: 将待审核文章撤回为草稿，允许重新编辑

**成功响应** (200):
```json
{ "message": "已撤回为草稿" }
```

**错误响应**:
- `400`: 只有待审核状态的文章可以撤回
- `403`: 无权操作此文章

**状态流转**: `PENDING` → `DRAFT`

**前端注意**:
- ✅ 仅在文章状态为 `pending` 时显示撤回按钮
- ✅ 撤回后可以重新编辑并提交
- ⚠️ 撤回后需要重新提交才能再次进入审核队列

### 5. 获取公开文章列表（分页）

**接口**: `GET /article/public/list?page=1&size=10&category_id=1`  
**权限**: 公开

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量 |
| category_id | int | null | 按分类筛选（可选） |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "title": "文章标题",
      "summary": "摘要...",
      "content_path": "storage/articles/a1b2c3d4.md",
      "status": "published",
      "published_at": "2026-04-25T10:00:00",
      "created_at": "2026-04-25T09:00:00",
      "category_id": 1,
      "category": { "id": 1, "name": "技术分享" }
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 5
}
```

**前端注意**:
- ✅ 仅返回已发布且未删除的文章（`status='published' AND deleted_at IS NULL`）
- ✅ 按 `created_at` 降序排列
- ✅ 返回统一的分页格式 `{items, total, page, pages}`
- ✅ 支持按分类筛选

---

### 6. 获取我的文章列表（分页）

**接口**: `GET /article/my/list?page=1&size=10&status=draft`  
**权限**: 所有登录用户

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量 |
| status | string | null | 按状态筛选（draft/pending/published，可选） |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "title": "我的草稿",
      "summary": "摘要...",
      "status": "draft",
      "submitted_at": null,
      "reviewed_at": null,
      "published_at": null,
      "created_at": "2026-04-25T10:00:00",
      "updated_at": "2026-04-25T10:00:00",
      "category_id": 1,
      "category": { "id": 1, "name": "技术分享" }
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

**前端注意**:
- ✅ 返回当前用户的所有文章（不包括已删除）
- ✅ 按 `created_at` 降序排列
- ✅ 可通过 `status` 参数筛选特定状态的文章
- ✅ 返回统一的分页格式 `{items, total, page, pages}`

---

### 7. 获取待审核文章列表（管理员）

**接口**: `GET /article/admin/pending`  
**权限**: 仅管理员

**功能**: 获取所有待审核的文章，按提交时间排序

**成功响应** (200):
```json
[
  {
    "id": 1,
    "title": "待审核文章",
    "summary": "摘要...",
    "status": "pending",
    "submitted_at": "2026-04-25T10:00:00",
    "created_at": "2026-04-25T09:00:00",
    "author": { 
      "id": 2, 
      "username": "testuser" 
    },
    "category": { 
      "id": 1, 
      "name": "技术分享" 
    }
  }
]
```

**前端注意**:
- ✅ 仅返回待审核状态的文章（`status='pending'`）
- ✅ 按 `submitted_at` 升序排列（先提交先处理）
- ✅ 预加载作者和分类信息
- ⚠️ 普通用户调用返回 403

---

### 8. 管理员审核文章

**接口**: `POST /article/admin/articles/{article_id}/review`  
**权限**: 仅管理员

**请求体**:
```json
{
  "pass_audit": true,
  "remark": null
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pass_audit | boolean | ✅ | `true`=通过，`false`=驳回 |
| remark | string | 条件必填 | 驳回时必须填写理由（最多500字符） |

**成功响应** (200):
```json
{ "message": "审核操作成功" }
```

**状态流转**:
- 通过: `PENDING` → `PUBLISHED`（设置 `reviewed_at`, `reviewed_by`, `published_at`）
- 驳回: `PENDING` → `DRAFT`（设置 `reviewed_at`, `reviewed_by`, `review_remark`）

**前端注意**:
- ⚠️ 驳回时必须填写理由
- ✅ 审核后可在文章详情中查看审核人和驳回理由
- ⚠️ 仅能审核状态为 `pending` 的文章

---

### 9. 上传图片

**接口**: `POST /article/upload-image`  
**权限**: 所有登录用户

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | 图片文件 |

**成功响应** (200):
```json
{
  "url": "/storage/images/a1b2c3d4.jpg"
}
```

**错误响应**:
- `400`: 只能上传图片文件 / 图片太大了（超过10MB）
- `500`: 图片保存失败

**前端注意**:
- ✅ 支持格式：jpg, jpeg, png, gif, webp 等
- ✅ 文件大小限制：10MB
- ✅ 返回的 URL 可直接用于 Markdown 插入：`![alt](http://127.0.0.1:8000/storage/images/a1b2c3d4.jpg)`

---

### 10. 移至回收站（软删除）

**接口**: `DELETE /article/{article_id}`  
**权限**: 文章作者或管理员

**功能**: 设置 `deleted_at`，文章从前台消失但数据保留

**成功响应** (200):
```json
{ "message": "已入回收站" }
```

**错误响应**:
- `400`: 文章已在回收站中
- `403`: 无权删除此文章
- `404`: 文章不存在

---

### 11. 恢复文章

**接口**: `POST /article/{article_id}/restore`  
**权限**: 文章作者或管理员

**功能**: 清除 `deleted_at`，文章重新可见

**成功响应** (200):
```json
{ "message": "已恢复" }
```

---

### 12. 彻底删除（硬删除）

**接口**: `DELETE /article/{article_id}/hard`  
**权限**: 文章作者或管理员

**⚠️ 警告**: 此操作不可逆！会删除数据库记录和物理文件

**成功响应** (200):
```json
{ "message": "文章已永久删除" }
```

**前端注意**:
- ⚠️ 执行前必须二次确认
- ⚠️ 删除后无法撤销

---

## 🏷️ 元数据管理模块（分类与标签）

### 权限说明
- **公开接口**：查看所有分类、查看所有标签
- **登录用户**：创建标签
- **管理员专属**：创建/删除分类、删除标签

---

### 1. 查看所有分类

**接口**: `GET /meta/categories`  
**权限**: 公开

**成功响应** (200):
```json
[
  { "id": 1, "name": "技术分享" },
  { "id": 2, "name": "生活随笔" }
]
```

---

### 2. 创建分类（管理员）

**接口**: `POST /meta/categories`  
**权限**: 仅管理员

**请求体**:
```json
{
  "name": "技术分享"
}
```

**成功响应** (200):
```json
{ "id": 1, "name": "技术分享" }
```

**错误响应**:
- `400`: 该分类名称已存在
- `403`: 权限不足

---

### 3. 删除分类（管理员）

**接口**: `DELETE /meta/categories/{cat_id}`  
**权限**: 仅管理员

**成功响应** (200):
```json
{ "message": "分类已删除" }
```

**⚠️ 警告**: 删除分类不会级联删除关联的文章，文章的 `category_id` 会变为 null

---

### 4. 查看所有标签

**接口**: `GET /meta/tags`  
**权限**: 公开

**成功响应** (200):
```json
[
  { "id": 1, "name": "FastAPI" },
  { "id": 2, "name": "Vue3" }
]
```

---

### 5. 创建标签（所有用户）

**接口**: `POST /meta/tags`  
**权限**: 所有登录用户

**请求体**:
```json
{
  "name": "FastAPI"
}
```

**成功响应** (200):
```json
{ "id": 1, "name": "FastAPI" }
```

**特殊行为**:
- ✅ 如果标签已存在，直接返回已有标签（不报错）
- ✅ 普通用户和管理员都可以创建标签
- ✅ 自动去重，避免数据库中出现重复标签

---

### 6. 修改标签（管理员）

**接口**: `PUT /meta/tags/{tag_id}`  
**权限**: 仅管理员

**请求体**:
```json
{
  "name": "Python"
}
```

**成功响应** (200):
```json
{ "id": 1, "name": "Python" }
```

**错误响应**:
- `400`: 该标签名称已存在
- `404`: 标签不存在

**注意**: 修改后，所有关联该标签的文章会自动同步显示新名称

---

### 7. 删除标签（管理员）

**接口**: `DELETE /meta/tags/{tag_id}`  
**权限**: 仅管理员

**成功响应** (200):
```json
{ "message": "标签已从系统中移除" }
```

**⚠️ 警告**: 
- 这是物理删除标签库条目
- 由于中间表设置了 `ON DELETE CASCADE`，删除标签会自动解除所有文章的关联
- 通常只有发现违规标签时才调用

---

## 👤 用户权限管理

### 调整用户角色（管理员）

**接口**: `PUT /article/admin/users/{target_user_id}/role`  
**权限**: 仅管理员

**请求体**:
```json
{
  "new_role": "admin"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 可选值 |
|------|------|------|--------|
| new_role | string | ✅ | `"admin"` 或 `"common"` |

**成功响应** (200):
```json
{ "message": "权限更新成功" }
```

**错误响应**:
- `400`: 不能修改自己的权限 / 系统必须保留至少一名管理员
- `404`: 用户不存在
- `422`: 参数验证失败（必须是 `admin` 或 `common`）

**前端注意**:
- ⚠️ 枚举值是小写字符串（`"admin"` 而非 `"ADMIN"`）
- ⚠️ 不能降级最后一个管理员
- ⚠️ 不能修改自己的角色

---

## 📊 完整业务流程示例

### 场景1: 普通用户创建并提交审核文章

```javascript
// Step 1: 自动保存草稿（使用 content 字段）
const saveResponse = await axios.post('/api/v1/article/autosave', {
  id: null,  // 新建文章
  title: '我的新文章',
  summary: '这是一篇测试文章',
  content: '# 我的新文章\n\n这是文章内容...',
  category_id: 1,
  tag_ids: [1, 2]
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

const articleId = saveResponse.data.id  // 注意：返回的是完整 Article 对象

// Step 2: 用户点击提交审核
await axios.put(`/api/v1/article/${articleId}/publish`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
// 响应: { "message": "已提交审核" }

// Step 3: 查看我的待审核文章
const myPending = await axios.get('/api/v1/article/my/list?status=pending&page=1&size=10', {
  headers: { 'Authorization': `Bearer ${token}` }
})
// 响应格式: { items: [...], total: 5, page: 1, pages: 1 }
```

### 场景2: 管理员审核文章

```javascript
// Step 1: 查看待审核列表
const pendingList = await axios.get('/api/v1/article/admin/pending', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
// [{ id: 1, title: '...', author: {...}, submitted_at: '...' }]

// Step 2: 审核通过
await axios.post(`/api/v1/article/admin/articles/${articleId}/review`, {
  pass_audit: true,
  remark: null
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
// 响应: { "message": "审核通过，文章已发布" }

// Step 3: 或者驳回（需要填写理由）
await axios.post(`/api/v1/article/admin/articles/${articleId}/review`, {
  pass_audit: false,
  remark: '内容需要进一步完善，请补充更多示例代码'
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
// 响应: { "message": "文章已驳回：内容需要进一步完善，请补充更多示例代码" }
```

### 场景3: 用户撤回文章重新编辑

```javascript
// Step 1: 撤回待审核文章
await axios.post(`/api/v1/article/${articleId}/withdraw`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
// 响应: { "message": "已撤回为草稿状态" }

// Step 2: 修改文章内容（使用 content 字段）
await axios.post('/api/v1/article/autosave', {
  id: articleId,  // 携带ID表示更新
  title: '修改后的标题',
  summary: '修改后的摘要',
  content: '# 修改后的文章\n\n这是更新后的内容...',
  category_id: 1,
  tag_ids: [1, 2, 3]
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// Step 3: 重新提交审核
await axios.put(`/api/v1/article/${articleId}/publish`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### 场景4: 管理员直接发布文章

```javascript
// 管理员创建文章后直接发布（跳过审核）
const saveResponse = await axios.post('/api/v1/article/autosave', {
  id: null,
  title: '管理员文章',
  summary: '无需审核',
  content: '# 管理员文章\n\n这是管理员直接发布的文章...',
  category_id: 1,
  tag_ids: [1]
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 直接发布
await axios.put(`/api/v1/article/${saveResponse.data.id}/publish`, {}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
// 响应: { "message": "发布成功" }
```

### 场景5: 防抖自动保存

```javascript
import { ref, watch } from 'vue'

const title = ref('')
const summary = ref('')
const content = ref('')  // 使用 content 而非 content_path
const categoryId = ref(1)
const tagIds = ref([1, 2])
const articleId = ref(null)
let saveTimer = null

// 监听内容变化，防抖保存
watch([title, summary, content], async () => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(async () => {
    try {
      const response = await axios.post('/api/v1/article/autosave', {
        id: articleId.value,  // null表示新建，有值表示更新
        title: title.value,
        summary: summary.value,
        content: content.value,  // 直接发送 Markdown 内容
        category_id: categoryId.value,
        tag_ids: tagIds.value
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // 新建文章时保存返回的 ID
      if (!articleId.value) {
        articleId.value = response.data.id  // 注意：返回完整 Article 对象
      }
      
      console.log('自动保存成功')
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('自动保存失败，请手动保存')
    }
  }, 2000)  // 停止输入2秒后保存
})

// 页面关闭前强制保存
window.addEventListener('beforeunload', async () => {
  if (saveTimer) clearTimeout(saveTimer)
  // 立即保存
  await saveArticle()
})
```

### 场景6: 图片上传与使用

```javascript
// 1. 选择图片文件
const fileInput = document.querySelector('input[type="file"]')
const file = fileInput.files[0]

// 2. 上传图片
const formData = new FormData()
formData.append('file', file)

const uploadResponse = await axios.post('/api/v1/article/upload-image', formData, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data'
  }
})

// 3. 获取图片 URL
const imageUrl = uploadResponse.data.url
// 例如: "/storage/images/a1b2c3d4.jpg"

// 4. 插入到 Markdown 编辑器
const markdownImage = `![${file.name}](http://127.0.0.1:8000${imageUrl})`
editor.insertText(markdownImage)
```

### 场景7: 管理分类和标签

```javascript
// 1. 获取所有分类（用于下拉选择）
const categories = await axios.get('/api/v1/meta/categories')
// [{ id: 1, name: '技术分享' }, ...]

// 2. 获取所有标签
const tags = await axios.get('/api/v1/meta/tags')
// [{ id: 1, name: 'FastAPI' }, ...]

// 3. 创建新标签（普通用户也可以）
const newTag = await axios.post('/api/v1/meta/tags', {
  name: 'Python'
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
// 如果标签已存在，直接返回已有标签

// 4. 管理员修改标签名称
await axios.put('/api/v1/meta/tags/1', {
  name: 'Python3'
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 5. 创建文章时绑定分类和标签（使用 content 字段）
await axios.post('/api/v1/article/autosave', {
  title: '我的文章',
  summary: '文章摘要',
  content: '# 内容...',
  category_id: 1,  // 选择分类
  tag_ids: [1, 2]  // 选择多个标签
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### 场景8: 管理员完整操作流程

```javascript
// 1. 查看所有待审核文章
const pendingList = await axios.get('/api/v1/article/admin/pending', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 2. 查看全站文章（分页）
const allArticles = await axios.get('/api/v1/article/admin/all?page=1&size=20', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
// 响应格式: { items: [...], total: 100, page: 1, pages: 5 }

// 3. 按状态筛选（只看草稿）
const drafts = await axios.get('/api/v1/article/admin/all?status=draft&page=1&size=10', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 4. 按作者筛选
const userArticles = await axios.get('/api/v1/article/admin/all?user_id=2&page=1&size=10', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 5. 审核通过
await axios.post(`/api/v1/article/admin/articles/${articleId}/review`, {
  pass_audit: true,
  remark: null
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 6. 或者驳回
await axios.post(`/api/v1/article/admin/articles/${articleId}/review`, {
  pass_audit: false,
  remark: '内容质量不高，需要改进'
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 7. 创建分类
await axios.post('/api/v1/meta/categories', {
  name: '新技术'
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})

// 8. 调整用户权限
await axios.put(`/api/v1/article/admin/users/${userId}/role`, {
  new_role: 'admin'  // 注意：小写字符串
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
})
```

---

## 💡 前端开发建议

### 1. 状态管理
建议使用 Pinia 管理文章编辑状态：
```javascript
// stores/article.js
export const useArticleStore = defineStore('article', {
  state: () => ({
    currentArticle: null,
    isDraft: true,
    lastSaved: null
  }),
  actions: {
    setArticle(article) {
      this.currentArticle = article
    },
    markAsPublished() {
      this.isDraft = false
    }
  }
})
```

### 2. Markdown 渲染
推荐使用以下库：
- **markdown-it**: 轻量级 Markdown 解析器
- **highlight.js**: 代码高亮
- **katex**: 数学公式支持

```javascript
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(str, { language: lang }).value
    }
    return ''
  }
})

const html = md.render(markdownContent)
```

### 3. 错误处理最佳实践

```javascript
// 统一错误处理拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    const { status, data } = error.response || {}
    
    switch (status) {
      case 401:
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
        break
      case 403:
        ElMessage.warning('权限不足，仅博主可操作')
        break
      case 404:
        ElMessage.error('文章不存在或已被删除')
        break
      case 429:
        ElMessage.warning('操作过于频繁，请稍后再试')
        break
      default:
        ElMessage.error(data?.detail || '请求失败')
    }
    
    return Promise.reject(error)
  }
)
```

---

## 💬 评论管理模块

### 权限说明
- **公开接口**：查看文章评论列表
- **登录用户**：发表评论、回复评论、删除自己的评论、举报评论
- **管理员专属**：删除任意评论、查看待处理举报、处理举报、全站评论巡查

### 核心功能概览
- 💬 **发表评论**：支持一级评论和嵌套回复
- 🗑️ **软删除**：作者或管理员可删除评论
- 🚩 **举报系统**：用户可举报不当评论
- 👮 **管理员审核**：查看和处理举报
- 🔍 **全站巡查**：管理员可查看所有评论

---

### 1. 发表评论/回复

**接口**: `POST /comments/articles/{article_id}/comments`  
**权限**: 所有登录用户

**请求体**:
```json
{
  "content": "这是一篇很棒的文章！",
  "parent_id": null
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | ✅ | 评论内容（1-1000字符） |
| parent_id | int | ❌ | 父评论ID，null表示一级评论 |

**成功响应** (200):
```json
{
  "id": 1,
  "content": "这是一篇很棒的文章！",
  "parent_id": null,
  "user_id": 1,
  "created_at": "2026-04-30T10:00:00",
  "author": {
    "id": 1,
    "username": "BaoZi"
  }
}
```

**错误响应**:
- `400`: 父评论不存在或不属于该文章
- `404`: 文章不存在

**前端注意**:
- ✅ 后审模式：评论直接可见，无需审核
- ✅ 回复评论时，`parent_id` 填写被回复评论的 ID
- ✅ 返回的 `author` 对象包含评论者信息

---

### 2. 获取文章评论列表

**接口**: `GET /comments/articles/{article_id}/comments`  
**权限**: 公开

**成功响应** (200):
```json
[
  {
    "id": 1,
    "content": "沙发！前排支持作者！",
    "parent_id": null,
    "user_id": 1,
    "created_at": "2026-04-30T10:00:00",
    "author": {
      "id": 1,
      "username": "BaoZi"
    }
  },
  {
    "id": 2,
    "content": "谢谢支持！",
    "parent_id": 1,
    "user_id": 2,
    "created_at": "2026-04-30T10:05:00",
    "author": {
      "id": 2,
      "username": "Admin"
    }
  }
]
```

**前端注意**:
- ✅ 仅返回已审核且未删除的评论（`is_audited=true AND deleted_at IS NULL`）
- ✅ 按 `created_at` 升序排列（旧评论在前）
- ✅ 扁平结构，前端需自行组装树形结构
- ✅ 通过 `parent_id` 判断是否为回复

---

### 3. 删除评论

**接口**: `DELETE /comments/{comment_id}`  
**权限**: 评论作者或管理员

**成功响应** (200):
```json
{
  "message": "评论已删除"
}
```

**错误响应**:
- `403`: 无权删除他人评论
- `404`: 评论不存在

**前端注意**:
- ✅ 普通用户只能删除自己的评论
- ✅ 管理员可以删除任意评论
- ✅ 采用软删除，数据仍保留在数据库中

---

### 4. 举报评论

**接口**: `POST /comments/{comment_id}/report`  
**权限**: 所有登录用户

**请求体**:
```json
{
  "reason": "评论内容包含不当言论"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reason | string | ✅ | 举报原因（2-200字符） |

**成功响应** (200):
```json
{
  "message": "举报成功，感谢您的监督"
}
```

**错误响应**:
- `400`: 您已举报过该评论，请耐心等待处理
- `404`: 被举报评论不存在

**前端注意**:
- ✅ 同一用户对同一评论只能举报一次（未处理前）
- ✅ 举报后需等待管理员处理
- ⚠️ 建议提供预设举报原因选项

---

### 5. 获取待处理举报列表（管理员）

**接口**: `GET /comments/admin/reports`  
**权限**: 仅管理员

**成功响应** (200):
```json
[
  {
    "id": 1,
    "reason": "评论内容包含不当言论",
    "is_resolved": false,
    "created_at": "2026-04-30T10:00:00",
    "comment": {
      "id": 5,
      "content": "违规内容...",
      "parent_id": null,
      "user_id": 3,
      "created_at": "2026-04-30T09:00:00",
      "author": {
        "id": 3,
        "username": "testuser"
      }
    },
    "reporter": {
      "id": 1,
      "username": "BaoZi"
    }
  }
]
```

**前端注意**:
- ✅ 仅返回未处理的举报（`is_resolved=false`）
- ✅ 按 `created_at` 降序排列（最新举报在前）
- ✅ 包含举报人、被举报评论的完整信息

---

### 6. 处理举报（管理员）

**接口**: `PUT /comments/admin/reports/{report_id}/resolve`  
**权限**: 仅管理员

**功能**: 标记举报为已处理

**成功响应** (200):
```json
{
  "message": "举报已标记为已处理"
}
```

**错误响应**:
- `404`: 举报记录不存在

**前端注意**:
- ✅ 处理后举报状态变为 `is_resolved=true`
- ✅ 处理后可选择是否删除被举报评论
- ⚠️ 此接口仅标记举报状态，不自动删除评论

---

### 7. 全站评论巡查（管理员）

**接口**: `GET /comments/admin/comments/all?page=1&size=20`  
**权限**: 仅管理员

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 20 | 每页数量 |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "content": "评论内容...",
      "parent_id": null,
      "user_id": 1,
      "created_at": "2026-04-30T10:00:00",
      "author": {
        "id": 1,
        "username": "BaoZi"
      }
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

**前端注意**:
- ✅ 返回所有评论（包括已删除）
- ✅ 按 `created_at` 降序排列
- ✅ 统一分页格式 `{items, total, page, pages}`
- ✅ 可用于内容审核和监控

---

## 💡 评论系统开发建议

### 1. 前端评论树形结构组装

```javascript
// 将扁平评论列表转换为树形结构
function buildCommentTree(comments) {
  const commentMap = new Map()
  const tree = []
  
  // 第一遍：建立映射
  comments.forEach(comment => {
    commentMap.set(comment.id, { ...comment, replies: [] })
  })
  
  // 第二遍：构建树形结构
  comments.forEach(comment => {
    if (comment.parent_id === null) {
      tree.push(commentMap.get(comment.id))
    } else {
      const parent = commentMap.get(comment.parent_id)
      if (parent) {
        parent.replies.push(commentMap.get(comment.id))
      }
    }
  })
  
  return tree
}

// 使用示例
const flatComments = await axios.get(`/api/v1/comments/articles/${articleId}/comments`)
const commentTree = buildCommentTree(flatComments.data)
```

### 2. 评论组件示例（Vue3）

```vue
<template>
  <div class="comments-section">
    <!-- 发表评论 -->
    <div class="comment-form">
      <textarea v-model="newComment" placeholder="写下你的评论..."></textarea>
      <button @click="submitComment" :disabled="loading">发表评论</button>
    </div>
    
    <!-- 评论列表 -->
    <div class="comment-list">
      <CommentItem 
        v-for="comment in commentTree" 
        :key="comment.id"
        :comment="comment"
        @reply="handleReply"
        @delete="handleDelete"
        @report="handleReport"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const articleId = ref(1)
const newComment = ref('')
const commentTree = ref([])
const loading = ref(false)

// 加载评论
const loadComments = async () => {
  const response = await axios.get(
    `/api/v1/comments/articles/${articleId.value}/comments`
  )
  commentTree.value = buildCommentTree(response.data)
}

// 发表评论
const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  loading.value = true
  try {
    await axios.post(
      `/api/v1/comments/articles/${articleId.value}/comments`,
      {
        content: newComment.value,
        parent_id: null
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    newComment.value = ''
    await loadComments() // 重新加载评论
  } catch (error) {
    console.error('评论失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadComments()
})
</script>
```

### 3. 举报功能实现

```javascript
// 举报评论
const reportComment = async (commentId, reason) => {
  try {
    await axios.post(
      `/api/v1/comments/${commentId}/report`,
      { reason },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    ElMessage.success('举报成功，感谢您的监督')
  } catch (error) {
    if (error.response?.status === 400) {
      ElMessage.warning('您已举报过该评论')
    } else {
      ElMessage.error('举报失败')
    }
  }
}

// 显示举报对话框
const showReportDialog = (commentId) => {
  ElMessageBox.prompt('请输入举报原因', '举报评论', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPattern: /.{2,200}/,
    inputErrorMessage: '举报原因至少2个字符，最多200个字符'
  }).then(({ value }) => {
    reportComment(commentId, value)
  })
}
```

### 4. 管理员举报处理界面

```javascript
// 获取待处理举报
const loadPendingReports = async () => {
  const response = await axios.get('/api/v1/comments/admin/reports', {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  })
  pendingReports.value = response.data
}

// 处理举报
const resolveReport = async (reportId) => {
  await axios.put(
    `/api/v1/comments/admin/reports/${reportId}/resolve`,
    {},
    {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    }
  )
  ElMessage.success('举报已标记为已处理')
  await loadPendingReports() // 刷新列表
}

// 同时删除被举报评论
const resolveAndDelete = async (reportId, commentId) => {
  // 先处理举报
  await axios.put(
    `/api/v1/comments/admin/reports/${reportId}/resolve`,
    {},
    {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    }
  )
  
  // 再删除评论
  await axios.delete(
    `/api/v1/comments/${commentId}`,
    {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    }
  )
  
  ElMessage.success('举报已处理，评论已删除')
  await loadPendingReports()
}
```

---

## 🔄 后续更新计划

- [ ] 文章搜索功能
- [ ] 文章版本历史
- [x] 图片上传与管理
- [x] 分类与标签管理（增删改查）
- [x] 完整审核流程（提交/撤回/审核/驳回）
- [x] 防灌水机制
- [x] 评论系统（发表/回复/删除/举报）
- [ ] 点赞与收藏

---

**最后更新时间**: 2026-04-19  
**文档版本**: v4.1  
**维护者**: Backend Team


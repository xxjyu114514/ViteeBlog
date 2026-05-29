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
2. 调用 `/auth/register` 携带验证码完成注册（注意请求体嵌套结构）

> ⚠️ 验证码一次性有效，校验后立即销毁
> ⚠️ **重要**：注册接口的请求体需要使用嵌套结构，因为后端使用了 `Body(embed=True)`

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

**请求体**（注意嵌套结构）:
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

**⚠️ 重要说明**:
- 由于后端使用了 `Body(embed=True)`，请求体必须是嵌套结构
- `user_in` 对象包含用户注册信息
- `email_code` 与 `user_in` 同级
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
- `400`: 验证码错误或已失效 / 用户名或邮箱已存在 / 该邮箱已注册
- `422`: 参数验证失败（查看具体字段错误）
- `500`: 服务器内部错误

---

### 4. 修改个人密码

**接口**: `PUT /auth/change-password`  
**权限**: 所有登录用户

**请求头**:
```
Authorization: Bearer <Your_Token>
```

**请求体**:
```json
{
  "old_password": "123456",
  "new_password": "newpassword123"
}
```

**成功响应** (200):
```json
{
  "message": "密码修改成功"
}
```

**错误响应**:
- `400`: 旧密码错误
- `401`: 未授权（Token无效或过期）

**前端注意**:
- ✅ 需要用户输入旧密码进行验证
- ✅ 新密码长度要求：6-128个字符
- ✅ 修改成功后建议提示用户重新登录

---

### 5. 发送找回密码验证码

**接口**: `POST /auth/forgot-password/send-code`

**请求体**:
```json
{
  "email": "user@example.com"
}
```

**成功响应** (200):
```json
{
  "message": "验证码已发送至您的邮箱，请查收"
}
```

**错误响应**:
- `400`: 该邮箱未注册
- `500`: 邮件发送失败

**前端注意**:
- ✅ 只有已注册的邮箱才能发送重置验证码
- ✅ 验证码有效期10分钟
- ✅ 点击后禁用按钮，开启60秒倒计时

---

### 6. 重置密码

**接口**: `POST /auth/forgot-password/reset`

**请求体**:
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newpassword123"
}
```

**参数约束**:
- `email`: 必须是已注册的邮箱
- `code`: 6位数字验证码
- `new_password`: 6-128个字符

**成功响应** (200):
```json
{
  "message": "密码重置成功，请使用新密码登录"
}
```

**错误响应**:
- `400`: 验证码错误、已失效或已被使用过
- `404`: 用户不存在
- `422`: 参数验证失败

**前端注意**:
- ✅ 需要先执行步骤5获取验证码
- ✅ 验证码一次性有效，使用后失效
- ✅ 重置成功后跳转到登录页

---

### 7. 注销个人账号

**接口**: `DELETE /auth/delete-account`  
**权限**: 所有登录用户（管理员除外）

**请求头**:
```
Authorization: Bearer <Your_Token>
```

**成功响应** (200):
```json
{
  "message": "账号已注销，感谢您的使用"
}
```

**错误响应**:
- `400`: 管理员账号不能注销，请先转让管理员权限
- `401`: 未授权

**前端注意**:
- ⚠️ **此操作不可逆**，必须二次确认
- ⚠️ 注销后 `is_active=False`，`deleted_at` 设置为当前时间
- ⚠️ 管理员账号不能直接注销，需先转移权限
- ℹ️ 注销后可以联系管理员恢复账号

---

### 8. 【超级管理员】修改用户角色

**接口**: `PUT /auth/admin/users/{user_id}/role`  
**权限**: 仅管理员

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 目标用户ID |

**请求头**:
```
Authorization: Bearer <Admin_Token>
```

**请求体**:
```json
{
  "new_role": "admin"
}
```

**可选值**:
- `"admin"`: 提升为管理员
- `"common"`: 降级为普通用户

**成功响应** (200):
```json
{
  "message": "成功将用户角色更新为 admin"
}
```

**错误响应**:
- `400`: 不能修改自己的角色 / 全站必须至少保留一名管理员
- `404`: 目标用户不存在
- `403`: 权限不足

**前端注意**:
- ⚠️ 不能修改自己的角色
- ⚠️ 降级最后一个管理员时会失败
- ✅ 枚举值是小写字符串（`"admin"` 而非 `"ADMIN"`）

---

### 9. 【管理员】恢复已注销账号

**接口**: `PUT /auth/admin/users/{user_id}/restore`  
**权限**: 仅管理员

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 被注销的用户ID |

**请求头**:
```
Authorization: Bearer <Admin_Token>
```

**成功响应** (200):
```json
{
  "message": "账号 BaoZi 已恢复"
}
```

**错误响应**:
- `400`: 该账号未被注销，无需恢复
- `404`: 用户不存在
- `403`: 权限不足

**前端注意**:
- ✅ 恢复后会设置 `is_active=True`，`deleted_at=None`
- ✅ 用户可以重新登录
- ⚠️ 只能恢复已注销的账号（`deleted_at` 不为 null）

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

### 3.1 修改个人资料

**接口**: `PUT /auth/update-profile`  
**权限**: 所有登录用户

**请求头**:
```
Authorization: Bearer <Your_Token>
```

**请求体**:
```json
{
  "username": "NewUsername",
  "avatar": "/storage/avatars/avatar_test.jpg"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ❌ | 新昵称（3-50个字符），可选 |
| avatar | string | ❌ | 头像URL，可选 |

**成功响应** (200):
```json
{
  "message": "个人资料更新成功",
  "username": "NewUsername",
  "avatar": "/storage/avatars/avatar_test.jpg"
}
```

**错误响应**:
- `400`: 该昵称已被占用
- `401`: 未授权（Token无效或过期）

**前端注意**:
- ✅ 可以只传 `username` 或只传 `avatar`，也可以同时修改
- ✅ 修改昵称时会检查是否与其他用户重名
- ✅ 头像URL通常通过上传接口获取后传入
- ⚠️ 用户名长度要求：3-50个字符

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

**最后更新时间**: 2026-05-05  
**文档版本**: v4.2  
**维护者**: Backend Team

---

## 📝 文章管理模块

### 权限说明
- **公开接口**：获取文章列表、获取文章详情、查看分类/标签
- **登录用户**：创建/编辑文章、上传图片、创建标签、提交审核
- **管理员专属**：审核文章、查看全站文章、调整用户权限、管理分类/标签

### 核心功能概览
- ✍️ **自动保存**：实时同步草稿到服务器（数据库存储，支持乐观锁）
- 🔒 **乐观锁机制**：防止多人同时编辑导致的内容覆盖
- 📝 **审核流程**：普通用户提交 → 管理员审核 → 发布/驳回
- 🔙 **撤回功能**：可撤回待审核文章重新编辑
- 🛡️ **防灌水**：普通用户最多3篇待审核文章
- 🗑️ **回收站机制**：软删除后数据保留
- ♻️ **恢复功能**：可从回收站恢复误删文章
- 💥 **硬删除**：永久粉碎文章记录
- 🖼️ **图片管理**：支持上传和删除图片

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
  "tag_ids": [1, 2],
  "cover_image": "/storage/images/abc123.jpg",
  "version": null
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | ❌ | 新建时为 null，更新时必填 |
| title | string | ❌ | 文章标题（1-200字符），可选 |
| summary | string | ❌ | 文章摘要（最多500字符） |
| content | string | ❌ | 文章内容（Markdown格式），直接存储到数据库 |
| category_id | int | ❌ | 分类ID，可选 |
| tag_ids | int[] | ❌ | 标签ID数组 |
| cover_image | string | ❌ | 封面图片URL（可选） |
| version | int | ❌ | 版本号（更新时用于乐观锁校验，新建时可忽略） |

**成功响应** (200):
```json
{
  "id": 1,
  "version": 1,
  "message": "已自动保存"
}
```

**错误响应**:
- `400`: 分类不存在 / 标题和内容不能同时为空
- `403`: 无权操作此文章
- `404`: 文章不存在
- `409`: 文章已被他人修改，请刷新后重新编辑（乐观锁冲突）

**前端注意**:
- ✅ 建议实现防抖保存（停止输入后2秒自动调用）
- ✅ 返回简化格式 `{id, version, message}`，使用 `response.body.id` 获取文章ID
- ✅ 文章内容直接存储在数据库 `content` 字段，无需单独读取文件
- ⚠️ **待审核状态（PENDING）下禁止编辑**，必须先撤回为草稿
- ⚠️ 保存草稿不会改变文章状态，状态由发布接口控制
- 🔒 **乐观锁机制**：更新文章时必须携带当前 `version`，如果版本不匹配会返回 409 错误
- ✅ 每次保存成功后，`version` 会自动递增，前端应更新本地缓存的版本号

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
  "content": "# Markdown 内容\n\n这是文章内容...",
  "cover_image": "/storage/images/abc123.jpg",
  "version": 1,
  "view_count": 100,
  "status": "published",
  "submitted_at": null,
  "reviewed_at": null,
  "published_at": "2026-04-25T10:00:00",
  "created_at": "2026-04-25T09:00:00",
  "updated_at": "2026-04-25T10:00:00",
  "deleted_at": null,
  "user_id": 1,
  "category_id": 1,
  "author": {
    "id": 1,
    "username": "BaoZi"
  },
  "category": { 
    "id": 1, 
    "name": "技术分享" 
  },
  "tags": [
    { "id": 1, "name": "FastAPI" }
  ]
}
```

**新增字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| cover_image | string | 封面图片URL，可为 null |
| view_count | int | 文章阅读量，每次访问自动+1 |
| author | object | 作者信息（id, username） |

**权限说明**:
- ✅ **已发布文章**：所有人可查看
- ✅ **草稿/待审核文章**：仅作者和管理员可查看
- ✅ **已删除文章**：仅作者和管理员可查看
- ❌ **未登录用户访问非公开文章**：返回 401
- ❌ **非作者访问他人非公开文章**：返回 403

**前端注意**:
- ✅ 返回 Article 对象，包含分类、标签等关联信息
- ✅ **直接包含文章内容** (`content` 字段)，无需额外请求
- ✅ 包含 `version` 字段，编辑时需携带用于乐观锁校验
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
2. ✅ 文章内容不能为空（检查数据库中的 content 字段）

**成功响应** (200) - 管理员:
```json
{ "message": "发布成功" }
```

**成功响应** (200) - 普通用户:
```json
{ "message": "已提交审核" }
```

**错误响应**:
- `400`: 发布失败：标题不能为空 / 文章内容不能为空
- `403`: 文章不存在或无权操作

**状态流转**:
- 管理员: `任何状态` → `PUBLISHED`
- 普通用户: `DRAFT/驳回` → `PENDING`

**前端注意**:
- ⚠️ 发布前确保标题和内容不为空
- ⚠️ 确保 autosave 已成功保存内容到数据库
- ✅ 建议在提交前提示用户确认
- ✅ 普通用户提交审核时，系统会自动清空之前的驳回理由

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
- ✅ 撤回后可继续编辑，编辑时注意携带最新的 `version`

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
      "cover_image": "/storage/images/abc123.jpg",
      "view_count": 150,
      "status": "published",
      "published_at": "2026-04-25T10:00:00",
      "created_at": "2026-04-25T09:00:00",
      "category_id": 1,
      "category": { "id": 1, "name": "技术分享" }
    }
  ],
  "total": 50,
  "page": 1,
  "size": 10,
  "pages": 5
}
```

**前端注意**:
- ✅ 仅返回已发布且未删除的文章（`status='published' AND deleted_at IS NULL`）
- ✅ 按 `created_at` 降序排列
- ✅ 返回统一的分页格式 `{items, total, page, size, pages}`
- ✅ 支持按分类筛选
- ✅ **新增字段**：
  - `cover_image`: 封面图片URL，可用于文章卡片展示
  - `view_count`: 阅读量统计，实时递增

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
      "cover_image": "/storage/images/abc123.jpg",
      "view_count": 50,
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
  "size": 10,
  "pages": 1
}
```

**前端注意**:
- ✅ 返回当前用户的所有文章（不包括已删除）
- ✅ 按 `created_at` 降序排列
- ✅ 可通过 `status` 参数筛选特定状态的文章
- ✅ 返回统一的分页格式 `{items, total, page, size, pages}`
- ✅ **新增字段**：`cover_image`（封面图）、`view_count`（阅读量）

---

### 7. 获取待审核文章列表（管理员）

**接口**: `GET /article/admin/pending`  
**权限**: 仅管理员

**功能**: 获取所有待审核的文章，按提交时间排序

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "title": "待审核文章",
      "summary": "摘要...",
      "cover_image": "/storage/images/abc123.jpg",
      "view_count": 10,
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
  ],
  "total": 5,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

**前端注意**:
- ✅ 仅返回待审核状态的文章（`status='pending'`）
- ✅ 按 `submitted_at` 升序排列（先提交先处理）
- ✅ 预加载作者和分类信息
- ✅ 返回分页格式 `{items, total, page, size, pages}`
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
- 通过: `PENDING` → `PUBLISHED`（设置 `reviewed_at`, `reviewed_by`, `published_at`，清空 `review_remark`）
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
- `400`: 只能上传图片文件 / 文件大小不能超过10MB
- `500`: 文件保存失败

**前端注意**:
- ✅ 支持格式：jpg, jpeg, png, gif, webp 等
- ✅ 文件大小限制：10MB
- ✅ 返回的 URL 可直接用于 Markdown 插入：`![alt](http://127.0.0.1:8000/storage/images/a1b2c3d4.jpg)`

---

### 10. 删除图片

**接口**: `DELETE /article/upload-image?filename=a1b2c3d4.jpg`  
**权限**: 所有登录用户

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filename | string | ✅ | 要删除的图片文件名 |

**成功响应** (200):
```json
{
  "message": "图片已删除"
}
```

**错误响应**:
- `404`: 图片不存在
- `500`: 删除文件时出错

**前端注意**:
- ⚠️ 删除图片前请确认该图片未被其他文章引用
- ⚠️ 此操作不可逆

---

### 11. 移至回收站（软删除）

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

### 12. 恢复文章

**接口**: `POST /article/{article_id}/restore`  
**权限**: 文章作者或管理员

**功能**: 清除 `deleted_at`，文章重新可见

**成功响应** (200):
```json
{ "message": "已恢复" }
```

---

### 13. 彻底删除（硬删除）

**接口**: `DELETE /article/{article_id}/hard`  
**权限**: 文章作者或管理员

**⚠️ 警告**: 此操作不可逆！会永久删除数据库记录

**成功响应** (200):
```json
{ "message": "文章已永久删除" }
```

**前端注意**:
- ⚠️ 执行前必须二次确认
- ⚠️ 删除后无法撤销
- ℹ️ 硬删除仅删除数据库记录，不再处理物理文件

---

### 14. 文章点赞/取消点赞

**接口**: `POST /article/{article_id}/like`  
**权限**: 所有登录用户

**功能**: 对文章进行点赞或取消点赞操作（切换状态）

**成功响应** (200):
```json
{
  "liked": true,
  "like_count": 15
}
```

**参数说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| liked | boolean | `true`=已点赞，`false`=已取消点赞 |
| like_count | int | 当前文章的总点赞数 |

**错误响应**:
- `404`: 文章不存在
- `400`: 操作过于频繁

**前端注意**:
- ✅ 该接口为切换操作：如果已点赞则取消，未点赞则点赞
- ✅ 返回最新的点赞状态和总数
- ⚠️ 需要登录才能点赞
- ℹ️ 数据库使用唯一索引防止重复点赞

---

### 15. 获取文章点赞数

**接口**: `GET /article/{article_id}/like/count`  
**权限**: 公开

**功能**: 获取指定文章的点赞数量

**成功响应** (200):
```json
{
  "article_id": 1,
  "like_count": 15
}
```

**前端注意**:
- ✅ 无需登录即可查询
- ✅ 可用于文章列表页展示点赞数
- ℹ️ 文章详情接口中也会返回点赞信息

---

### 16. 单篇导入文章（管理员）

**接口**: `POST /article/admin/import/single`  
**权限**: 仅管理员

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | 支持 .txt、.md、.docx 格式 |

**文件大小限制**: 10MB

**文件解析规则**:
- **.txt**: 第一个长度1-100的非空行作为标题，其余为内容
- **.md**: 第一个以 `# ` 开头的行作为标题，全文为内容
- **.docx**: 第一个 Heading 1 样式段落或加粗段落作为标题

**成功响应** (200):
```json
{
  "article_id": 123,
  "title": "导入的文章标题",
  "message": "文章导入成功，请前往草稿箱编辑"
}
```

**错误响应**:
- `400`: 不支持的文件格式 / 文件大小超过限制
- `500`: 导入失败（详细错误信息）

**前端注意**:
- ✅ 导入的文章自动保存为草稿状态（`status='draft'`）
- ✅ 自动生成摘要（从内容中提取前200字符）
- ✅ 作者为当前管理员
- ⚠️ 导入后需前往草稿箱完善分类、标签等信息
- ℹ️ 摘要会自动去除 Markdown 标记符号

---

### 17. 批量导入文章（管理员）

**接口**: `POST /article/admin/import/batch`  
**权限**: 仅管理员

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | File[] | ✅ | 多个文件数组，支持 .txt、.md、.docx |

**总大小限制**: 50MB

**成功响应** (200):
```json
{
  "total": 10,
  "success": 8,
  "failed": [
    {
      "filename": "error.doc",
      "reason": "不支持的文件格式"
    }
  ],
  "articles": [
    {
      "article_id": 123,
      "title": "第一篇文章"
    },
    {
      "article_id": 124,
      "title": "第二篇文章"
    }
  ]
}
```

**参数说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 总共尝试导入的文件数 |
| success | int | 成功导入的数量 |
| failed | array | 失败的文件列表（含原因） |
| articles | array | 成功导入的文章ID和标题 |

**错误处理**:
- ✅ 单个文件失败不影响其他文件
- ✅ 每个文件独立事务，互不干扰
- ⚠️ 不支持的格式会记录到 `failed` 列表

**前端注意**:
- ✅ 可一次性上传多个文件
- ✅ 返回详细的成功/失败统计
- ✅ 失败文件包含具体原因，便于提示用户
- ℹ️ 所有导入的文章均为草稿状态

---

### 18. 批量上传图片（管理员）

**接口**: `POST /article/admin/upload-images/batch`  
**权限**: 仅管理员

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | ZIP 压缩包（.zip 格式） |

**文件大小限制**: 50MB

**支持的图片格式**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**成功响应** (200):
```json
{
  "total": 20,
  "success": 18,
  "failed": [
    {
      "filename": "readme.txt",
      "reason": "不是图片格式"
    }
  ],
  "urls": [
    "/storage/images/a1b2c3d4.jpg",
    "/storage/images/e5f6g7h8.png",
    "/storage/images/i9j0k1l2.webp"
  ]
}
```

**参数说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | ZIP 中处理的文件总数 |
| success | int | 成功上传的图片数量 |
| failed | array | 非图片或处理失败的文件列表 |
| urls | array | 成功上传的图片 URL 列表 |

**错误响应**:
- `400`: 只支持.zip格式 / 文件大小超过限制 / 无效的zip文件
- `500`: 处理失败

**前端注意**:
- ✅ 将多张图片打包成 ZIP 后上传
- ✅ 自动过滤非图片文件
- ✅ 返回所有图片的 URL，可直接用于文章
- ✅ 文件名自动生成 UUID，避免冲突
- ⚠️ ZIP 解压后的目录结构会被忽略，所有图片平铺到 `storage/images/`
- ℹ️ 适合批量迁移旧博客图片资源

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
// Step 1: 自动保存草稿（使用 content 字段，支持乐观锁）
const saveResponse = await axios.post('/api/v1/article/autosave', {
  id: null,  // 新建文章
  title: '我的新文章',
  summary: '这是一篇测试文章',
  content: '# 我的新文章\n\n这是文章内容...',
  category_id: 1,
  tag_ids: [1, 2],
  version: null  // 新建时为 null
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

const articleId = saveResponse.data.id  // 获取文章ID
let currentVersion = saveResponse.data.version  // 保存当前版本号

// Step 2: 用户点击提交审核
await axios.put(`/api/v1/article/${articleId}/publish`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
// 响应: { "message": "已提交审核" }
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

// Step 2: 修改文章内容（使用 content 字段，携带版本号）
await axios.post('/api/v1/article/autosave', {
  id: articleId,  // 携带ID表示更新
  title: '修改后的标题',
  summary: '修改后的摘要',
  content: '# 修改后的文章\n\n这是更新后的内容...',
  category_id: 1,
  tag_ids: [1, 2, 3],
  version: currentVersion  // 携带当前版本号进行乐观锁校验
}, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(response => {
  // 更新本地版本号
  currentVersion = response.data.version
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
const content = ref('')  // 使用 content 字段
const categoryId = ref(1)
const tagIds = ref([1, 2])
const articleId = ref(null)
const currentVersion = ref(null)  // 当前版本号
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
        tag_ids: tagIds.value,
        version: currentVersion.value  // 携带版本号
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // 新建文章时保存返回的 ID 和 version
      if (!articleId.value) {
        articleId.value = response.data.id
      }
      currentVersion.value = response.data.version  // 更新版本号
      
      console.log('自动保存成功')
    } catch (error) {
      if (error.response?.status === 409) {
        ElMessage.warning('文章已被他人修改，请刷新后重新编辑')
        // 这里可以触发重新加载文章逻辑
      } else {
        console.error('保存失败:', error)
        ElMessage.error('自动保存失败，请手动保存')
      }
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

// 5. 如需删除图片
await axios.delete('/api/v1/article/upload-image', {
  params: { filename: 'a1b2c3d4.jpg' },
  headers: { 'Authorization': `Bearer ${token}` }
})
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
const response = await axios.post('/api/v1/article/autosave', {
  title: '我的文章',
  summary: '文章摘要',
  content: '# 内容...',
  category_id: 1,  // 选择分类
  tag_ids: [1, 2]  // 选择多个标签
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
currentVersion = response.data.version  // 保存版本号
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
- **登录用户**：发表评论、回复评论、删除自己的评论、举报评论、点赞/取消点赞
- **管理员专属**：删除任意评论、查看待处理举报、处理举报、全站评论巡查

### 核心功能概览
- 💬 **发表评论**：支持一级评论和嵌套回复
- 👍 **点赞功能**：用户可点赞/取消点赞评论
- 🗑️ **软删除**：作者或管理员可删除评论
- 🚩 **举报系统**：用户可举报不当评论
- 👮 **管理员审核**：查看和处理举报
- 🔍 **全站巡查**：管理员可查看所有评论

### 数据模型

#### Comment（评论表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评论ID（主键） |
| content | text | 评论内容 |
| user_id | int | 评论者ID（外键关联User） |
| article_id | int | 文章ID（外键关联Article） |
| parent_id | int/null | 父评论ID，null表示一级评论 |
| is_audited | bool | 是否已审核（默认true） |
| created_at | datetime | 创建时间 |
| deleted_at | datetime/null | 删除时间（软删除） |

**关系**:
- `author`: 关联 User 表（评论者）
- `article`: 关联 Article 表（所属文章）
- `parent`: 自关联父评论
- `replies`: 自关联子评论列表
- `likes`: 关联 CommentLike 表（点赞记录）

#### CommentLike（评论点赞表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 点赞ID（主键） |
| comment_id | int | 评论ID（外键） |
| user_id | int | 用户ID（外键） |
| created_at | datetime | 点赞时间 |

**约束**: `(comment_id, user_id)` 唯一约束，防止重复点赞

#### CommentReport（评论举报表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 举报ID（主键） |
| comment_id | int | 被举报评论ID |
| reporter_id | int | 举报人ID |
| reason | string | 举报原因（2-200字符） |
| is_resolved | bool | 是否已处理（默认false） |
| created_at | datetime | 举报时间 |

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
  },
  "like_count": 0,
  "is_liked": false
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评论ID |
| content | string | 评论内容 |
| parent_id | int/null | 父评论ID，null表示一级评论 |
| user_id | int | 评论者ID |
| created_at | datetime | 创建时间 |
| author | object | 评论者信息（id, username） |
| like_count | int | 点赞数 |
| is_liked | bool | 当前用户是否已点赞（未登录时为false） |

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
    },
    "like_count": 5,
    "is_liked": true
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
    },
    "like_count": 2,
    "is_liked": false
  }
]
```

**前端注意**:
- ✅ 仅返回已审核且未删除的评论（`is_audited=true AND deleted_at IS NULL`）
- ✅ 按 `created_at` 升序排列（旧评论在前）
- ✅ 扁平结构，前端需自行组装树形结构
- ✅ 通过 `parent_id` 判断是否为回复
- ✅ 包含点赞数 `like_count` 和当前用户点赞状态 `is_liked`
- ✅ 未登录用户 `is_liked` 始终为 false

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

### 4. 点赞/取消点赞

**接口**: `POST /comments/{comment_id}/like`  
**权限**: 所有登录用户

**功能**: 切换点赞状态（已点赞则取消，未点赞则添加）

**成功响应** (200):
```json
{
  "liked": true,
  "like_count": 6
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| liked | bool | 当前操作后的点赞状态（true=已点赞，false=已取消） |
| like_count | int | 最新的点赞总数 |

**错误响应**:
- `404`: 评论不存在或已被删除

**前端注意**:
- ✅ 点击点赞按钮时调用此接口，无需区分点赞/取消
- ✅ 后端自动判断当前状态并切换
- ✅ 返回最新的点赞数和状态，前端直接更新UI
- ✅ 使用唯一约束防止重复点赞
- ⚠️ 需要登录才能点赞

---

### 5. 举报评论

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

### 6. 获取待处理举报列表（管理员）

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

### 7. 处理举报（管理员）

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

### 8. 全站评论巡查（管理员）

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
        @like="handleLike"
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

// 点赞/取消点赞
const handleLike = async (commentId) => {
  try {
    const response = await axios.post(
      `/api/v1/comments/${commentId}/like`,
      {},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    // 更新本地状态
    const { liked, like_count } = response.data
    updateCommentLikeStatus(commentId, liked, like_count)
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('评论不存在')
    } else if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

// 更新评论点赞状态（递归查找）
const updateCommentLikeStatus = (commentId, isLiked, likeCount) => {
  const updateNode = (nodes) => {
    for (let node of nodes) {
      if (node.id === commentId) {
        node.is_liked = isLiked
        node.like_count = likeCount
        return true
      }
      if (node.replies && node.replies.length > 0) {
        if (updateNode(node.replies)) return true
      }
    }
    return false
  }
  updateNode(commentTree.value)
}

onMounted(() => {
  loadComments()
})
</script>
```

### 3. 点赞功能实现

```javascript
// 点赞按钮组件
const LikeButton = {
  template: `
    <button 
      class="like-btn" 
      :class="{ 'liked': comment.is_liked }"
      @click="handleLike"
    >
      <span class="icon">{{ comment.is_liked ? '❤️' : '🤍' }}</span>
      <span class="count">{{ comment.like_count }}</span>
    </button>
  `,
  props: ['comment'],
  emits: ['like'],
  setup(props, { emit }) {
    const handleLike = () => {
      emit('like', props.comment.id)
    }
    return { handleLike }
  }
}

// 父组件中的处理函数
const handleLike = async (commentId) => {
  try {
    const response = await axios.post(
      `/api/v1/comments/${commentId}/like`,
      {},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    const { liked, like_count } = response.data
    // 更新UI状态
    updateCommentLikeStatus(commentId, liked, like_count)
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
      // 跳转到登录页
    }
  }
}
```

### 4. 举报功能实现

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

### 5. 管理员举报处理界面

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

## ⭐ 文章收藏模块

### 权限说明
- **登录用户**：收藏/取消收藏文章、查看我的收藏列表、检查收藏状态
- **公开接口**：无（所有收藏相关接口均需登录）

### 核心功能概览
- ⭐ **收藏切换**：一键收藏/取消收藏，自动判断当前状态
- 📋 **收藏列表**：分页查看我收藏的所有文章
- ✅ **状态检查**：快速检查是否已收藏某篇文章

---

### 1. 收藏/取消收藏文章

**接口**: `POST /favorites/{article_id}/favorite`  
**权限**: 所有登录用户

**功能**: 智能切换收藏状态（未收藏则收藏，已收藏则取消）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| article_id | int | ✅ | 文章ID |

**成功响应** (200) - 首次收藏:
```json
{
  "favorited": true,
  "message": "收藏成功"
}
```

**成功响应** (200) - 取消收藏:
```json
{
  "favorited": false,
  "message": "已取消收藏"
}
```

**错误响应**:
- `404`: 文章不存在或未公开发布（草稿、待审核、已删除的文章无法收藏）
- `401`: 未登录

**前端注意**:
- ✅ 接口自动判断当前收藏状态并切换
- ✅ 只能收藏已发布且未删除的文章
- ✅ 返回 `favorited` 字段表示操作后的状态
- ⚠️ 需要携带 Token 认证

---

### 2. 获取我的收藏列表

**接口**: `GET /favorites/my?page=1&size=10`  
**权限**: 所有登录用户

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量 |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "created_at": "2026-05-08T10:00:00",
      "article": {
        "id": 28,
        "title": "收藏的文章标题",
        "summary": "文章摘要...",
        "status": "published",
        "created_at": "2026-05-07T09:00:00"
      }
    }
  ],
  "total": 15,
  "page": 1,
  "size": 10,
  "pages": 2
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 收藏记录列表 |
| items[].id | int | 收藏记录ID |
| items[].created_at | datetime | 收藏时间 |
| items[].article | object | 被收藏的文章信息 |
| items[].article.id | int | 文章ID |
| items[].article.title | string | 文章标题 |
| items[].article.summary | string | 文章摘要 |
| items[].article.status | string | 文章状态 |
| items[].article.created_at | datetime | 文章创建时间 |
| total | int | 总记录数 |
| page | int | 当前页码 |
| size | int | 每页数量 |
| pages | int | 总页数 |

**前端注意**:
- ✅ 按收藏时间降序排列（最新收藏在前）
- ✅ 统一分页格式 `{items, total, page, size, pages}`
- ✅ 包含文章的简化信息（不包含正文内容）
- ⚠️ 如果文章被删除，可能仍会出现在收藏列表中

---

### 3. 检查收藏状态

**接口**: `GET /favorites/check/{article_id}`  
**权限**: 所有登录用户

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| article_id | int | ✅ | 文章ID |

**成功响应** (200):
```json
{
  "favorited": true
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| favorited | bool | 当前用户是否已收藏该文章 |

**前端注意**:
- ✅ 用于在文章详情页显示收藏按钮状态
- ✅ 返回简单的布尔值，便于UI更新
- ⚠️ 需要登录才能调用

---

## 💡 收藏功能开发建议

### 1. 收藏按钮组件（Vue3）

```vue
<template>
  <button 
    class="favorite-btn" 
    :class="{ 'favorited': isFavorited }"
    @click="toggleFavorite"
    :disabled="loading"
  >
    <span class="icon">{{ isFavorited ? '⭐' : '☆' }}</span>
    <span class="text">{{ isFavorited ? '已收藏' : '收藏' }}</span>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  articleId: {
    type: Number,
    required: true
  }
})

const isFavorited = ref(false)
const loading = ref(false)

// 检查收藏状态
const checkFavoriteStatus = async () => {
  try {
    const response = await axios.get(
      `/api/v1/favorites/check/${props.articleId}`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    isFavorited.value = response.data.favorited
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }
  
  loading.value = true
  try {
    const response = await axios.post(
      `/api/v1/favorites/${props.articleId}/favorite`,
      {},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    // 更新本地状态
    isFavorited.value = response.data.favorited
    ElMessage.success(response.data.message)
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('文章不存在或未发布')
    } else if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (token) {
    checkFavoriteStatus()
  }
})
</script>

<style scoped>
.favorite-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.favorite-btn.favorited {
  background: #fff3cd;
  border-color: #ffc107;
  color: #856404;
}

.favorite-btn:hover:not(:disabled) {
  background: #f8f9fa;
}

.favorite-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
```

### 2. 我的收藏页面

```vue
<template>
  <div class="my-favorites">
    <h2>我的收藏</h2>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="favorites.length === 0" class="empty">
      暂无收藏文章
    </div>
    
    <div v-else class="favorite-list">
      <div 
        v-for="item in favorites" 
        :key="item.id"
        class="favorite-item"
      >
        <router-link :to="`/article/${item.article.id}`">
          <h3>{{ item.article.title }}</h3>
          <p>{{ item.article.summary }}</p>
        </router-link>
        <div class="meta">
          <span class="time">收藏于 {{ formatDate(item.created_at) }}</span>
          <button @click="removeFavorite(item.article.id)">取消收藏</button>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="loadPage(currentPage - 1)"
        :disabled="currentPage === 1"
      >上一页</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button 
        @click="loadPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
      >下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const favorites = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 加载收藏列表
const loadFavorites = async (page = 1) => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/favorites/my', {
      params: { page, size: pageSize.value },
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    favorites.value = response.data.items
    total.value = response.data.total
    currentPage.value = response.data.page
  } catch (error) {
    console.error('加载收藏列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 翻页
const loadPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    loadFavorites(page)
  }
}

// 取消收藏
const removeFavorite = async (articleId) => {
  try {
    await axios.post(
      `/api/v1/favorites/${articleId}/favorite`,
      {},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    ElMessage.success('已取消收藏')
    // 重新加载列表
    await loadFavorites(currentPage.value)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadFavorites()
})
</script>
```

### 3. Axios 拦截器处理未登录

```javascript
// 在文章详情页自动检查登录状态
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 收藏相关接口的401错误
      if (error.config.url.includes('/favorites/')) {
        ElMessageBox.confirm(
          '您需要登录才能使用收藏功能',
          '提示',
          {
            confirmButtonText: '去登录',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          router.push('/login')
        })
      }
    }
    return Promise.reject(error)
  }
)
```

---

## 👤 用户个人主页模块

### 功能概述
个人主页模块提供用户公开信息的展示接口，包含用户基本信息、统计数据、文章列表等功能。

**核心特性**:
- 📊 **统计数据**: 文章总数、总点赞数、总阅读量、总收藏数、总评论数、最后活跃时间
- 📝 **文章列表**: 分页获取用户发布的公开文章
- 🔔 **社交状态**: 显示关注数、粉丝数、当前用户是否已关注
- 🆔 **公开访问**: 无需登录即可查看他人主页（登录后显示更多交互信息）

---

### ⚙️ 通用规范

**Base URL**: `/api/v1/users`  
**鉴权**: 基础信息无需登录，部分字段需登录才能查看  
**分页格式**: `{items, total, page, size, pages}`

---

### 1. 获取用户个人主页信息

**接口**: `GET /users/{user_id}`  
**权限**: 公开（未登录可查看基础信息，登录后显示 `is_following` 状态）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 目标用户ID |

**请求头**:
```
Authorization: Bearer <Token>  // 可选，登录后才有 is_following 字段
```

**成功响应** (200):
```json
{
  "id": 6,
  "username": "Van",
  "avatar": null,
  "bio": "这是一个热爱技术的全栈开发者",
  "following_count": 0,
  "followers_count": 0,
  "is_following": false,
  "created_at": "2026-05-09T17:17:10",
  "total_articles": 1,
  "total_likes_received": 1,
  "total_views": 0,
  "total_favorites": 0,
  "total_comments": 3,
  "last_active_at": "2026-05-17T21:17:22"
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| username | string | 用户名 |
| avatar | string/null | 头像URL |
| bio | string/null | 个人简介（最多200字符） |
| following_count | int | 关注数 |
| followers_count | int | 粉丝数 |
| is_following | boolean | 当前用户是否关注了该用户（仅登录后返回） |
| created_at | datetime | 注册时间 |
| total_articles | int | 文章总数（仅统计已发布且未删除的文章） |
| total_likes_received | int | 收到的总点赞数（所有文章的点赞总和） |
| total_views | int | 总阅读量（所有文章的浏览量总和） |
| total_favorites | int | 文章被收藏的总次数 |
| total_comments | int | 文章收到的总评论数（仅统计已审核通过的评论） |
| last_active_at | datetime/null | 最后活跃时间（最新文章的发布时间） |

**错误响应**:
- `404`: 用户不存在或已注销

**前端注意**:
- ✅ 未登录时 `is_following` 默认为 `false`
- ✅ 所有统计数据仅计算 `status='published' AND deleted_at IS NULL` 的文章
- ✅ `total_comments` 仅统计 `is_audited=true` 的评论
- ✅ 可用于用户个人主页、文章作者卡片等场景
- ✅ 建议缓存用户主页数据，避免频繁请求

---

### 2. 获取用户的文章列表

**接口**: `GET /users/{user_id}/articles?page=1&size=10`  
**权限**: 公开

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 目标用户ID |

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量（最大50） |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 35,
      "title": "评论功能测试文章",
      "summary": "用于测试评论系统的文章",
      "cover_image": null,
      "view_count": 0,
      "like_count": 0,
      "created_at": "2026-05-17T21:17:20"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 文章列表 |
| items[].id | int | 文章ID |
| items[].title | string | 文章标题 |
| items[].summary | string/null | 文章摘要 |
| items[].cover_image | string/null | 封面图片URL |
| items[].view_count | int | 阅读量 |
| items[].like_count | int | 点赞数 |
| items[].created_at | datetime | 创建时间 |
| total | int | 文章总数 |
| page | int | 当前页码 |
| size | int | 每页数量 |
| pages | int | 总页数 |

**错误响应**:
- `404`: 用户不存在或已注销

**前端注意**:
- ✅ 仅返回 `status='published' AND deleted_at IS NULL` 的文章
- ✅ 按 `created_at` 降序排列（最新文章在前）
- ✅ 统一分页格式 `{items, total, page, size, pages}`
- ✅ 可用于个人主页的"文章"标签页
- ✅ 预加载了 `tags` 关系，但简化输出中不包含

---

### 💡 个人主页开发建议

#### 1. 用户主页组件结构

```vue
<template>
  <div class="user-profile">
    <!-- 用户基本信息 -->
    <div class="profile-header">
      <img :src="user.avatar || defaultAvatar" class="avatar" />
      <h2>{{ user.username }}</h2>
      <p v-if="user.bio" class="bio">{{ user.bio }}</p>
      <div class="stats">
        <span>文章 {{ user.total_articles }}</span>
        <span>获赞 {{ user.total_likes_received }}</span>
        <span>阅读 {{ user.total_views }}</span>
        <span>收藏 {{ user.total_favorites }}</span>
        <span>评论 {{ user.total_comments }}</span>
      </div>
      <div class="social-stats">
        <span>关注 {{ user.following_count }}</span>
        <span>粉丝 {{ user.followers_count }}</span>
      </div>
      <!-- 关注按钮（仅登录且非本人可见） -->
      <button 
        v-if="isLoggedIn && !isSelf" 
        @click="toggleFollow"
        :class="{ 'following': user.is_following }"
      >
        {{ user.is_following ? '已关注' : '关注' }}
      </button>
    </div>
    
    <!-- 文章列表 -->
    <div class="article-list">
      <ArticleCard 
        v-for="article in articles" 
        :key="article.id"
        :article="article"
      />
      <!-- 分页 -->
      <Pagination 
        :current="currentPage" 
        :total="totalPages"
        @change="loadArticles"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
})

const user = ref(null)
const articles = ref([])
const currentPage = ref(1)
const totalPages = ref(0)
const isLoggedIn = ref(!!token)
const isSelf = ref(false)

// 加载用户信息
const loadUserProfile = async () => {
  try {
    const response = await axios.get(`/api/v1/users/${props.userId}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    user.value = response.data
    isSelf.value = user.value.id === currentUserId
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载文章列表
const loadArticles = async (page = 1) => {
  try {
    const response = await axios.get(`/api/v1/users/${props.userId}/articles`, {
      params: { page, size: 10 }
    })
    articles.value = response.data.items
    totalPages.value = response.data.pages
    currentPage.value = response.data.page
  } catch (error) {
    console.error('加载文章列表失败:', error)
  }
}

// 切换关注状态
const toggleFollow = async () => {
  try {
    if (user.value.is_following) {
      // 取消关注
      await axios.delete(`/api/v1/social/follow/${props.userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      user.value.is_following = false
      user.value.followers_count--
    } else {
      // 关注
      await axios.post(`/api/v1/social/follow/${props.userId}`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      user.value.is_following = true
      user.value.followers_count++
    }
  } catch (error) {
    console.error('操作失败:', error)
  }
}

onMounted(() => {
  loadUserProfile()
  loadArticles()
})
</script>
```

#### 2. 统计数据实时更新

```javascript
// 当用户发表新文章后，刷新主页数据
const handleArticlePublished = async () => {
  await loadUserProfile()  // 重新加载统计数据
  await loadArticles(1)    // 重新加载文章列表
}

// 当文章被点赞/收藏/评论时，局部更新统计数据
const updateStats = (type, delta) => {
  if (type === 'likes') {
    user.value.total_likes_received += delta
  } else if (type === 'views') {
    user.value.total_views += delta
  } else if (type === 'favorites') {
    user.value.total_favorites += delta
  } else if (type === 'comments') {
    user.value.total_comments += delta
  }
}
```

#### 3. 性能优化建议

- ✅ **缓存策略**: 用户主页数据变化不频繁，建议使用 Pinia/Vuex 缓存
- ✅ **懒加载**: 文章列表使用虚拟滚动或无限加载
- ✅ **按需加载**: 首次仅加载基础信息，切换到"文章"标签时再加载文章列表
- ✅ **防抖处理**: 关注/取消关注操作添加防抖，防止重复点击

#### 4. 边界情况处理

- ⚠️ 用户不存在时显示 404 页面
- ⚠️ 用户已注销时提示"该账号已注销"
- ⚠️ 没有文章时显示空状态提示
- ⚠️ 统计数据为 0 时正常显示，不要隐藏

---

## 🔄 后续更新计划

- [ ] 文章搜索功能
- [ ] 文章版本历史
- [x] 图片上传与管理
- [x] 分类与标签管理（增删改查）
- [x] 完整审核流程（提交/撤回/审核/驳回）
- [x] 防灌水机制
- [x] 评论系统（发表/回复/删除/举报）
- [x] 点赞与收藏
- [x] 个人主页与统计数据

---

---

## 👥 社交关注系统

### 功能概述
社交关注系统允许用户之间建立关注关系，支持关注/取消关注、查看关注列表和粉丝列表等功能。

**核心特性**:
- 🔔 **关注/取消关注**: 一键关注感兴趣的用户
- 📋 **关注列表**: 查看自己或他人关注的用户
- 👥 **粉丝列表**: 查看自己或他人的粉丝
- 🔄 **互关状态**: 智能显示当前用户是否已关注列表中的人
- 📊 **分页查询**: 支持高效的分页加载

---

### ⚙️ 通用规范

**Base URL**: `/api/v1/social`  
**鉴权**: 所有接口均需登录（携带 `Authorization: Bearer <Token>`）  
**分页格式**: 统一使用 `{total, items}` 结构

---

### 1. 关注用户

**接口**: `POST /social/follow/{user_id}`  
**权限**: 所有登录用户

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 要关注的目标用户ID |

**请求头**:
```
Authorization: Bearer <Token>
```

**成功响应** (200):
```json
{
  "message": "关注成功"
}
```

**错误响应**:
- `400`: 你不能关注你自己 / 你已经关注了该用户
- `404`: 目标用户不存在或已注销
- `500`: 关注操作失败

**前端注意**:
- ✅ 关注前检查 `user_id != current_user.id`
- ✅ 重复关注会返回友好提示，不会报错
- ✅ 关注成功后自动更新用户的 `following_count` 和目标的 `followers_count`

---

### 2. 取消关注

**接口**: `DELETE /social/follow/{user_id}`  
**权限**: 所有登录用户

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 要取消关注的目标用户ID |

**请求头**:
```
Authorization: Bearer <Token>
```

**成功响应** (200):
```json
{
  "message": "已取消关注"
}
```

**错误响应**:
- `400`: 你尚未关注该用户
- `500`: 取消关注失败

**前端注意**:
- ✅ 取消关注后自动递减计数
- ✅ 使用 `max(0, count - 1)` 防止负数
- ✅ 建议在用户个人主页显示"已关注"按钮，点击后调用此接口

---

### 3. 获取某人的关注列表

**接口**: `GET /social/following/{user_id}?page=1&size=10`  
**权限**: 所有登录用户（未登录也可查看，但无 `is_following` 字段）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 目标用户ID |

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量（最大50） |

**请求头**:
```
Authorization: Bearer <Token>  // 可选，登录后才有 is_following 字段
```

**成功响应** (200):
```json
{
  "total": 25,
  "items": [
    {
      "id": 3,
      "username": "tech_guru",
      "email": "tech@example.com",
      "role": "common",
      "created_at": "2026-04-20T10:00:00",
      "avatar": null,
      "is_following": true  // 仅登录后可见，表示当前用户是否关注了此人
    },
    {
      "id": 5,
      "username": "code_master",
      "email": "code@example.com",
      "role": "common",
      "created_at": "2026-04-22T15:30:00",
      "avatar": null,
      "is_following": false
    }
  ]
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| total | int | 关注总数 |
| items | array | 用户列表 |
| is_following | boolean | 当前用户是否关注了该用户（仅登录后返回） |

**前端注意**:
- ✅ 未登录时 `is_following` 字段不返回或为 `false`
- ✅ 登录后后端会批量查询当前用户与列表中用户的关注关系
- ✅ 空列表防护：当 `target_ids` 为空时，跳过 SQL 查询避免报错
- ✅ 可用于展示"他关注的人"页面

---

### 4. 获取某人的粉丝列表

**接口**: `GET /social/followers/{user_id}?page=1&size=10`  
**权限**: 所有登录用户（未登录也可查看，但无 `is_following` 字段）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | ✅ | 目标用户ID |

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码（从1开始） |
| size | int | 10 | 每页数量（最大50） |

**请求头**:
```
Authorization: Bearer <Token>  // 可选，登录后才有 is_following 字段
```

**成功响应** (200):
```json
{
  "total": 100,
  "items": [
    {
      "id": 8,
      "username": "fan_user_1",
      "email": "fan1@example.com",
      "role": "common",
      "created_at": "2026-04-18T09:00:00",
      "avatar": null,
      "is_following": true  // 当前用户是否回关了此粉丝
    },
    {
      "id": 12,
      "username": "fan_user_2",
      "email": "fan2@example.com",
      "role": "common",
      "created_at": "2026-04-19T11:20:00",
      "avatar": null,
      "is_following": false
    }
  ]
}
```

**前端注意**:
- ✅ `is_following` 表示当前用户是否关注了这些粉丝（回关状态）
- ✅ 可用于实现"互相关注"标识
- ✅ 空列表防护同上
- ✅ 可用于展示"他的粉丝"页面

---

### 🚀 开发注意事项

#### 1. 关注状态实时更新
- ✅ 关注/取消关注后，前端应立即更新 UI 状态
- ✅ 建议维护本地缓存，避免频繁请求
- ✅ 在用户个人主页、文章作者信息等场景动态显示关注按钮

#### 2. 分页加载优化
- ✅ 使用无限滚动或传统分页器
- ✅ 首次加载建议 `size=10`，后续可增加到 `20-50`
- ✅ 当 `items.length < size` 时，说明已到最后一页

#### 3. 互关逻辑处理
- ✅ 如果 `is_following=true`，显示"已关注"或"互相关注"
- ✅ 如果 `is_following=false`，显示"关注"按钮
- ✅ 在自己的粉丝列表中，如果 `is_following=true`，可显示"已回关"

#### 4. 性能优化
- ✅ 后端已使用 `IN` 查询批量检查关注关系，避免 N+1 问题
- ✅ 前端应避免在循环中单独请求每个用户的关注状态
- ✅ 可使用虚拟列表渲染大量粉丝/关注列表

#### 5. 边界情况处理
- ⚠️ 不能关注自己（后端已校验）
- ⚠️ 不能关注已注销的用户（`is_active=False`）
- ⚠️ 重复关注会返回友好提示，前端应隐藏错误弹窗
- ⚠️ 取消关注不存在的记录会返回 400，前端应静默处理

---

## 💬 频道广场聊天系统

### 功能概述
频道广场是一个实时聊天系统，支持多频道管理、图文混合消息、引用回复、消息撤回等功能。

**核心特性**:
- 📢 **多频道管理**: 管理员可创建/删除频道，用户自由选择加入
- 🖼️ **多媒体支持**: 支持文本、图片、视频等多种媒体类型
- 💬 **引用回复**: 支持单级引用回复，方便上下文讨论
- ↩️ **消息撤回**: 2分钟内可撤回消息，撤回后可重新编辑
- 🔄 **无限滚动**: 基于游标的分页加载，流畅的聊天体验
- 🔒 **权限控制**: 仅管理员可管理频道，所有登录用户可发言

---

### ⚙️ 通用全局规范

**Base URL**: `/api/v1`  
**鉴权**: 除特定管理员接口外，所有请求均需携带请求头 `Authorization: Bearer <Token>`  
**媒体附件白名单**: URL 必须符合 `http://`, `https://`, `/storage/`, `data:` 四大前缀，否则返回 422  
**内容清洗**: 纯空格内容会被后端自动转为 null（拒绝空气消息）

---

### 一、频道管理（仅限管理员）

#### 1. 创建频道

**接口**: `POST /channels`  
**权限**: 仅管理员

**请求体**:
```json
{
  "name": "技术交流平台"
}
```

**成功响应** (201):
```json
{
  "id": 1,
  "name": "技术交流平台",
  "created_at": "2026-05-22T19:44:30",
  "allowed_user_ids": null
}
```

**错误响应**:
- `400`: 频道名称已存在
- `403`: 权限不足

**前端注意**:
- ✅ 频道名称必须唯一
- ✅ 保存返回的 `id` 用于后续操作

---

#### 2. 获取所有频道列表

**接口**: `GET /channels`  
**权限**: 所有登录用户

**成功响应** (200):
```json
[
  {
    "id": 1,
    "name": "技术交流平台",
    "created_at": "2026-05-22T19:44:30",
    "allowed_user_ids": null
  }
]
```

**前端注意**:
- ✅ 按创建时间升序排列
- ✅ 可用于频道切换下拉菜单

---

#### 3. 更新频道名称

**接口**: `PUT /channels/{channel_id}`  
**权限**: 仅管理员

**请求体**:
```json
{
  "name": "新技术讨论区"
}
```

**成功响应** (200):
```json
{
  "message": "频道名称已更新"
}
```

**错误响应**:
- `400`: 频道名称已存在
- `403`: 权限不足
- `404`: 频道不存在

---

#### 4. 删除频道

**接口**: `DELETE /channels/{channel_id}`  
**权限**: 仅管理员

**成功响应** (204): `No Content`

**⚠️ 高危警示**:
- ❌ **物理删除**：频道及其所有留言将被永久删除（CASCADE 级联删除）
- ❌ **不可恢复**：删除后无法找回数据
- ✅ **前端必须弹出二次确认框**，要求用户输入频道名称进行匹配验证

**错误响应**:
- `403`: 权限不足
- `404`: 频道不存在

---

### 二、核心发言与留言流（全员开放）

#### 5. 发送频道留言

**接口**: `POST /channels/{channel_id}/messages`  
**权限**: 所有登录用户

**请求体示例**（纯文本）:
```json
{
  "content": "大家好，今天我们来讨论一下 FastAPI 的性能优化",
  "media_attachments": null,
  "quote_message_id": null
}
```

**请求体示例**（图文混合 + 引用回复）:
```json
{
  "content": "我同意你的观点",
  "media_attachments": [
    {
      "type": "image",
      "url": "/storage/images/abc123.jpg"
    }
  ],
  "quote_message_id": 5
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 条件必填 | 文本内容（最多2000字符），与 media_attachments 至少填一个 |
| media_attachments | array | 条件必填 | 媒体附件数组，与 content 至少填一个 |
| quote_message_id | int | ❌ | 引用的消息ID（可选） |

**media_attachments 结构**:
```json
{
  "type": "image",  // 可选值: "image", "video", "file"
  "url": "/storage/images/abc123.jpg"  // 必须符合白名单规则
}
```

**成功响应** (201):
```json
{
  "id": 7,
  "channel_id": 2,
  "user_id": 5,
  "content": "这是一条测试消息",
  "media_attachments": [
    {
      "type": "image",
      "url": "/storage/images/abc123.jpg"
    }
  ],
  "created_at": "2026-05-22T19:53:34",
  "sender": {
    "id": 5,
    "username": "user114514",
    "avatar": null
  },
  "quote_message_id": null,
  "quoted_message": null
}
```

**🔒 安全校验**:
1. ✅ **空气消息防护**：content 和 media_attachments 不能同时为空
2. ✅ **内容清洗**：纯空格内容会被自动转为 null
3. ✅ **长度限制**：content 最多2000字符
4. ✅ **URL白名单**：仅支持 `http://`, `https://`, `/storage/`, `data:` 前缀

**错误响应**:
- `400`: 文本内容与媒体附件不能同时为空 / 引用的消息不存在
- `403`: 权限不足
- `404`: 频道不存在
- `422`: 参数验证失败（URL格式不合法等）

**前端注意**:
- ✅ 发送前校验：至少填写文本或附件之一
- ✅ 采用"先传文件拿到 URL，再发消息绑定 URL"的两阶段解耦设计
- ✅ 发送后自动滚动到底部
- ✅ 引用回复时显示被引用消息的预览

---

#### 6. 获取频道留言流（游标分页）

**接口**: `GET /channels/{channel_id}/messages?limit=50&before_id=null`  
**权限**: 所有登录用户

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 50 | 每页数量（最大100） |
| before_id | int | null | 游标ID，获取此ID之前的历史消息（用于向上滚动加载） |

**成功响应** (200):
```json
{
  "items": [
    {
      "id": 9,
      "channel_id": 2,
      "user_id": 3,
      "content": "历史消息",
      "media_attachments": null,
      "created_at": "2026-05-22T19:59:00",
      "sender": {
        "id": 3,
        "username": "testuser",
        "avatar": null
      },
      "quote_message_id": null,
      "quoted_message": null
    },
    {
      "id": 10,
      "channel_id": 2,
      "user_id": 5,
      "content": "最新消息",
      "media_attachments": null,
      "created_at": "2026-05-22T20:00:00",
      "sender": {
        "id": 5,
        "username": "user114514",
        "avatar": null
      },
      "quote_message_id": null,
      "quoted_message": null
    }
  ],
  "has_more": true,
  "next_cursor": 9
}
```

**✅ 瀑布流联动逻辑（重要）**:

1. **首次加载**：不传 `before_id`，后端返回最新 50 条消息
2. **数组排序**：`items` 内部已按**时间升序**排列（ID 从小到大，旧消息在上，新消息在下）
3. **直接渲染**：前端无需倒序，直接追加到聊天窗口底部
4. **向上滚动触顶**：当 `has_more=true` 时，将 `next_cursor` 作为 `before_id` 继续请求更早的历史记录
5. **加载完成**：当 `has_more=false` 时，说明已加载完所有历史消息

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 消息列表（按时间升序排列） |
| has_more | boolean | 是否还有更多历史消息 |
| next_cursor | int/null | 下一页的游标ID（传入 before_id 参数） |

**前端注意**:
- ✅ 符合主流聊天软件（微信、Slack）体验：最新消息在最底下，往上翻看历史
- ✅ 已撤回的消息不会出现在列表中
- ✅ 使用虚拟列表（Virtual List）渲染，避免几千个 DOM 节点硬卡

---

### 三、撤回与重新编辑（仅限作者本人）

#### 7. 消息撤回

**接口**: `POST /channels/messages/{message_id}/withdraw`  
**权限**: 消息作者本人

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message_id | int | ✅ | 消息ID |

**成功响应** (200):
```json
{
  "status": "success",
  "message": "消息撤回成功",
  "message_id": 123
}
```

**⏱️ 撤回规则**:
- ✅ 仅能撤回自己发送的消息
- ✅ 撤回时限：发送后2分钟内（后端采用服务器本地时钟校验）
- ✅ 撤回后消息从留言流中隐去（软删除）
- ✅ 超出时限锁死并返回 400

**错误响应**:
- `400`: 超过2分钟撤回时限 / 消息已被撤回
- `403`: 无权撤回他人消息
- `404`: 消息不存在

**前端注意**:
- ⚠️ 必须在消息旁边显示倒计时（2分钟）
- ✅ 超时后隐藏撤回按钮
- ✅ 撤回成功后，前端应立刻闪现"重新编辑"气泡

---

#### 8. 获取撤回内容（重新编辑反填）

**接口**: `GET /channels/messages/{message_id}/re-edit`  
**权限**: 消息作者本人

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message_id | int | ✅ | 已撤回的消息ID |

**成功响应** (200):
```json
{
  "content": "这是撤回前的内容",
  "media_attachments": [
    {
      "type": "image",
      "url": "/storage/images/abc123.jpg"
    }
  ]
}
```

**错误响应**:
- `400`: 消息未被撤回 / 不是撤回者本人
- `403`: 权限不足
- `404`: 消息不存在

**前端注意**:
- ✅ 撤回成功后立即调用此接口获取原内容
- ✅ 将内容一键反填回输入框，允许用户修改后重新发送
- ⚠️ 仅在撤回后的短时间内有效（建议2分钟内）

---

### 四、防灌水频率控制

#### 9. 获取个人待审核文章数

**接口**: `GET /article/my/pending-count`  
**权限**: 所有登录用户

**成功响应** (200):
```json
{
  "pending_count": 2
}
```

**策略**:
- ✅ 普通用户待审核池上限为 3 篇
- ✅ 前端在路由跳转或点击"提交审核"前，应优先读取此阈值拦截恶意灌水

---

### 🚀 极简开发备忘（前端必读）

#### 1. 多媒体发送流程
采用**两阶段解耦设计**：
1. 先调用上传图片接口拿到 URL
2. 再调用发送消息接口绑定 URL

#### 2. 防爆舱渲染
聊天室信息流极大时，**必须使用虚拟列表（Virtual List）滚动**，严禁几千个 DOM 节点硬卡。

#### 3. 引用跳转逻辑
- 点击留言中的 `quoted_message` 区域，前端应计算其 `id` 并高亮跳转至对应时序流位置
- 若引用的消息已被撤回，文本统一硬编码显示 `[该消息已被撤回]`

#### 4. 消息状态管理
- ✅ 前端应维护本地消息缓存，避免重复请求
- ✅ 新消息到达时自动滚动到底部
- ✅ 使用 WebSocket 可实现实时更新（当前版本暂不支持）

#### 5. 安全性
- ⚠️ 所有媒体URL必须经过白名单校验
- ⚠️ 防止 XSS 攻击：对用户输入的内容进行转义
- ⚠️ 频率限制：防止恶意刷屏（后端已实现）

---

**最后更新时间**: 2026-05-22  
**文档版本**: v5.0  
**维护者**: Backend Team

##### 感谢所有贡献者！

##
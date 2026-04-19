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

> ⚠️ **权限要求**：除获取公开列表和文章详情外，其他接口均需 `admin` 角色

### 核心功能概览
- ✍️ **自动保存**：实时同步草稿到服务器（文件 + 数据库）
- 🗑️ **回收站机制**：软删除30天后自动清理
- ♻️ **恢复功能**：可从回收站恢复误删文章
- 💥 **硬删除**：永久粉碎文章及物理文件

---

### 1. 自动保存/更新文章

**接口**: `POST /article/autosave`

**权限**: `admin` 仅

**功能说明**:
- 新建文章时自动生成 Markdown 文件并创建数据库记录
- 更新文章时同步修改文件和数据库
- 支持标签关联和分类设置

**请求体**:
```json
{
  "title": "我的第一篇文章",
  "content": "# Hello World\n\n这是文章内容...",
  "article_id": null,
  "category_id": 1,
  "tag_ids": [1, 2, 3]
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ✅ | 文章标题 |
| content | string | ✅ | Markdown 格式内容 |
| article_id | int | ❌ | 文章ID（新建时为 null，更新时必填） |
| category_id | int | ❌ | 分类ID |
| tag_ids | int[] | ❌ | 标签ID数组 |

**成功响应** (200):
```json
{
  "article_id": 1,
  "url": "/static/storage/articles/user5_1776582611.md",
  "message": "内容已同步"
}
```

**错误响应**:
- `403`: 无权操作此文章（非作者）
- `500`: 文件系统或数据库写入失败

**前端注意**:
- ✅ 建议实现防抖保存（用户停止输入后2-3秒自动调用）
- ✅ 也可定期保存（如每30秒）
- ✅ 页面关闭前务必调用一次确保数据不丢失
- ⚠️ 新建文章返回 `article_id`，后续更新需携带此 ID

---

### 2. 获取文章详情

**接口**: `GET /article/{article_id}`

**权限**: 公开（已删除文章返回404）

**成功响应** (200):
```json
{
  "info": {
    "id": 1,
    "title": "我的第一篇文章",
    "summary": "Hello World 这是文章内容...",
    "status": "published",
    "view_count": 42,
    "published_at": "2026-04-19T10:00:00",
    "author": { "id": 5, "username": "BaoZi" },
    "category": { "id": 1, "name": "技术分享" },
    "tags": [
      { "id": 1, "name": "FastAPI" },
      { "id": 2, "name": "Python" }
    ]
  },
  "content": "# Hello World\n\n这是文章内容..."
}
```

**错误响应**:
- `404`: 文章不存在或已被删除

**前端注意**:
- ✅ 每次访问会自动增加阅读计数（`view_count`）
- ✅ `content` 字段为原始 Markdown，需前端渲染
- ⚠️ 已软删除的文章无法访问

---

### 3. 发布文章

**接口**: `PUT /article/{article_id}/publish`

**权限**: `admin` 仅（且必须为文章作者）

**功能说明**:
- 将草稿状态改为已发布
- 设置发布时间（`published_at`）
- 若在回收站中，会自动恢复

**成功响应** (200):
```json
{
  "message": "文章已发布"
}
```

**错误响应**:
- `404`: 文章不存在或无权操作

---

### 4. 获取公开文章列表

**接口**: `GET /article/list/public`

**权限**: 公开

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category_id | int | ❌ | 按分类筛选 |

**请求示例**:
```
GET /article/list/public?category_id=1
```

**成功响应** (200):
```json
[
  {
    "id": 1,
    "title": "我的第一篇文章",
    "summary": "Hello World 这是文章内容...",
    "status": "published",
    "view_count": 42,
    "published_at": "2026-04-19T10:00:00",
    "category_id": 1
  },
  {
    "id": 2,
    "title": "第二篇文章",
    "summary": "...",
    "status": "published",
    "view_count": 15,
    "published_at": "2026-04-18T15:30:00",
    "category_id": 2
  }
]
```

**前端注意**:
- ✅ 返回列表按 `published_at` 降序排列（最新的在前）
- ✅ 仅返回已发布且未删除的文章
- ✅ 不包含文章正文（`content`），需单独请求详情接口

---

### 5. 移至回收站（软删除）

**接口**: `DELETE /article/{article_id}`

**权限**: `admin` 仅（且必须为文章作者）

**功能说明**:
- 设置 `deleted_at` 时间戳，文章从前台消失
- 数据和物理文件仍然保留
- 可在回收站中查看和恢复

**成功响应** (200):
```json
{
  "message": "已移至回收站"
}
```

**错误响应**:
- `404`: 文章不存在或无权操作

---

### 6. 查看回收站

**接口**: `GET /article/recycle-bin/list`

**权限**: `admin` 仅

**功能说明**:
- 返回当前用户所有已软删除的文章
- **自动清理**：超过30天的文章会被永久删除（包括物理文件）

**成功响应** (200):
```json
[
  {
    "id": 1,
    "title": "已删除的文章",
    "deleted_at": "2026-04-19T10:00:00",
    "status": "draft",
    "view_count": 42
  }
]
```

**前端注意**:
- ✅ 每次调用会自动清理30天前的过期文章
- ✅ 可用于实现“回收站”页面
- ⚠️ 清理操作不可逆

---

### 7. 恢复文章

**接口**: `POST /article/{article_id}/restore`

**权限**: `admin` 仅（且必须为文章作者）

**功能说明**:
- 将 `deleted_at` 设为 `NULL`
- 文章重新出现在前台和列表中

**成功响应** (200):
```json
{
  "message": "文章已恢复"
}
```

**错误响应**:
- `404`: 文章不存在或未被删除（无需恢复）

---

### 8. 彻底删除（硬删除）

**接口**: `DELETE /article/{article_id}/hard`

**权限**: `admin` 仅（且必须为文章作者）

**⚠️ 警告**: 此操作不可逆！

**功能说明**:
1. 删除磁盘上的 Markdown 文件
2. 从数据库中永久删除记录
3. 无法恢复

**成功响应** (200):
```json
{
  "message": "文章及其文件已永久从服务器删除"
}
```

**错误响应**:
- `404`: 文章不存在或无权操作

**前端注意**:
- ⚠️ 执行前必须二次确认（弹窗提示）
- ✅ 建议仅在回收站页面提供此功能
- ⚠️ 删除后无法撤销

---

## 📊 完整业务流程示例

### 场景1: 创建并发布文章

```javascript
// Step 1: 自动保存草稿
const saveResponse = await axios.post('/api/v1/article/autosave', {
  title: '我的新文章',
  content: '# 内容...',
  article_id: null,  // 新建
  category_id: 1,
  tag_ids: [1, 2]
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

const articleId = saveResponse.data.article_id

// Step 2: 用户点击发布
await axios.put(`/api/v1/article/${articleId}/publish`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// Step 3: 刷新列表
const listResponse = await axios.get('/api/v1/article/list/public')
```

### 场景2: 编辑已有文章

```javascript
// 自动保存（携带 article_id）
await axios.post('/api/v1/article/autosave', {
  title: '更新后的标题',
  content: '更新后的内容...',
  article_id: existingArticleId,  // 关键：携带ID
  category_id: 1,
  tag_ids: [1, 2, 3]
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### 场景3: 删除与恢复

```javascript
// 1. 软删除
await axios.delete(`/api/v1/article/${articleId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 2. 查看回收站
const recycleBin = await axios.get('/api/v1/article/recycle-bin/list', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 3. 恢复文章
await axios.post(`/api/v1/article/${articleId}/restore`, {}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 4. 永久删除（谨慎操作！）
if (confirm('确定要永久删除吗？此操作不可恢复！')) {
  await axios.delete(`/api/v1/article/${articleId}/hard`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
}
```

### 场景4: 防抖自动保存

```javascript
import { ref, watch } from 'vue'

const content = ref('')
const articleId = ref(null)
let saveTimer = null

// 监听内容变化，防抖保存
watch(content, (newContent) => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(async () => {
    try {
      const response = await axios.post('/api/v1/article/autosave', {
        title: title.value,
        content: newContent,
        article_id: articleId.value,
        category_id: categoryId.value,
        tag_ids: tagIds.value
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      // 新建文章时保存返回的 ID
      if (!articleId.value) {
        articleId.value = response.data.article_id
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

## 🔄 后续更新计划

- [ ] 文章搜索功能
- [ ] 文章版本历史
- [ ] 富文本编辑器支持
- [ ] 图片上传与管理
- [ ] 评论系统
- [ ] 点赞与收藏

---

**最后更新时间**: 2026-04-19  
**文档版本**: v3.0  
**维护者**: Backend Team

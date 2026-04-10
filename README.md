# ViteeBlog - 个人博客系统开发完全指南

## 项目概述

ViteeBlog 是一个现代化的沉浸式个人博客系统，采用前后端分离架构。前端基于 Vue 3 + Vite 实现独特的滚轮导航体验，后端基于 Python FastAPI 提供高性能 RESTful API。

**核心特色**：
- **沉浸式导航**: 支持鼠标滚轮在主要页面间横向切换
- **双层级架构**: 1级沉浸式页面 + 2级详情页面
- **现代化技术栈**: Vue 3 Composition API + FastAPI 异步支持
- **安全防护**: JWT认证 + 登录失败锁定机制

## 项目上下文与设计哲学

### 设计目标
1. **用户体验优先**: 通过沉浸式滚轮导航提供独特的浏览体验
2. **开发效率**: 现代化工具链支持快速开发和热重载
3. **可维护性**: 清晰的架构分层和模块化设计
4. **安全性**: 多层次安全防护机制

### 架构决策说明
- **为什么选择 Vue 3 + Vite**: 更快的构建速度、更好的开发体验、Composition API 的逻辑复用优势
- **为什么选择 FastAPI**: 自动生成 API 文档、类型安全、异步支持、高性能
- **为什么采用双层级页面**: 平衡沉浸式体验与功能性需求

## 开发环境搭建

### 前置依赖
- **Node.js**: v18+ (推荐使用 nvm 管理)
- **Python**: 3.9+ (推荐使用 pyenv 管理)
- **MySQL**: 8.0+ (或其他兼容 MySQL 的数据库)
- **包管理器**: npm (前端), pip (后端)

### 前端环境配置

#### 1. 安装依赖
```bash
cd frontend
npm install
```

#### 2. 环境变量配置
创建 `.env` 文件（如果需要自定义配置）：
```env
# Vite 环境变量示例
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### 3. 开发命令
```bash
# 启动开发服务器 (默认 http://localhost:5173)
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 运行测试 (如果有)
npm test
```

### 后端环境配置

#### 1. 创建虚拟环境
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
# 如果没有 requirements.txt，根据 package.json 推断主要依赖：
pip install fastapi uvicorn sqlalchemy alembic python-jose[cryptography] passlib[bcrypt] email-validator python-dotenv
```

#### 3. 数据库配置
创建 `.env` 文件：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password  
DB_NAME=viteeblog

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 4. 数据库初始化
```bash
# 初始化 Alembic
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "initial_tables"

# 应用迁移
alembic upgrade head
```

#### 5. 后端开发命令
```bash
# 启动开发服务器 (默认 http://localhost:8000)
uvicorn main:app --reload

# 生成 API 文档
# 访问 http://localhost:8000/docs (Swagger UI)
# 访问 http://localhost:8000/redoc (ReDoc)
```

## 项目架构详解

### 前端架构

#### 目录结构说明
```
frontend/
├── src/
│   ├── assets/              # 静态资源文件
│   │   └── main.scss        # 全局 SCSS 样式
│   ├── components/          # 可复用组件
│   │   ├── Navbar.vue       # 导航栏组件 - 核心交互组件
│   │   ├── PostItem.vue     # 单个文章卡片组件
│   │   └── PostList.vue     # 文章列表容器组件
│   ├── composables/         # 组合式函数 (逻辑复用核心)
│   │   ├── usePageTransition.js    # 页面过渡动画状态管理
│   │   └── usePrimaryPageWheel.js  # 滚轮导航核心逻辑
│   ├── layout/              # 布局组件
│   │   └── FrontLayout.vue  # 主布局 - 包含导航栏和路由视图
│   ├── router/              # 路由配置
│   │   └── index.js         # 路由定义 - 包含页面层级元信息
│   ├── views/               # 页面视图组件
│   │   ├── HomeView.vue                 # 首页 (1级沉浸式)
│   │   ├── PostsImmersiveView.vue       # 文章列表沉浸式 (1级)
│   │   ├── PostListView.vue             # 文章详情 (2级)
│   │   ├── AboutImmersiveView.vue       # 关于沉浸式 (1级)  
│   │   ├── AboutView.vue                # 关于详情 (2级)
│   │   ├── MessageImmersiveView.vue     # 留言沉浸式 (1级)
│   │   ├── MessageView.vue              # 留言详情 (2级)
│   │   └── LoginView.vue                # 登录页面 (特殊页面)
│   ├── App.vue              # 根组件 - 应用入口点
│   ├── main.js              # 应用初始化 - 创建 Vue 实例和 Pinia store
│   └── style.css            # 全局 CSS 样式
├── vite.config.js           # Vite 配置 - 包含路径别名配置
├── package.json             # 依赖和脚本配置
└── index.html               # HTML 模板
```

#### 核心概念详解

##### 1. 页面层级系统
**1级页面 (沉浸式页面)**:
- **路由命名**: 以 `-immersive` 结尾 (`/posts-immersive`)
- **meta.index**: 0, 1, 2, 3 (连续小数字)
- **功能特点**: 
  - 支持滚轮导航
  - 沉浸式透明导航栏
  - 横向滑动动画
- **当前页面列表**:
  - `home` (index: 0) → `/`
  - `posts-immersive` (index: 1) → `/posts-immersive`  
  - `about-immersive` (index: 2) → `/about-immersive`
  - `message-immersive` (index: 3) → `/message-immersive`

**2级页面 (详情页面)**:
- **路由命名**: 无特殊后缀 (`/posts`)
- **meta.index**: 10, 20, 30 (大数字，避免参与滚轮导航)
- **功能特点**:
  - 不支持滚轮导航
  - 标准实色导航栏
  - 独立进入/退出动画
  - 必须包含返回按钮

##### 2. 滚轮导航实现原理
在 `src/composables/usePrimaryPageWheel.js` 中：

```javascript
// 页面顺序严格定义
const pageOrder = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']

// 滚轮事件处理
const handleWheel = (e) => {
  if (isAnimating.value) return // 动画期间锁定
  
  e.preventDefault()
  
  // 向上滚动：返回前一页 (currentIndex > 0)
  if (e.deltaY < 0 && currentIndex > 0) {
    router.push(pageOrder[currentIndex - 1])
  }
  // 向下滚动：进入下一页 (currentIndex < 最后索引)
  else if (e.deltaY > 0 && currentIndex < pageOrder.length - 1) {
    router.push(pageOrder[currentIndex + 1])
  }
}
```

**关键约束**:
- 线性单向流动，不支持跳跃
- 边界检查防止越界
- 动画状态锁定防止重复触发

##### 3. 路由元信息设计
在 `src/router/index.js` 中，每个路由都包含 `meta` 属性：

```javascript
{
  path: '/posts-immersive',
  name: 'posts-immersive', 
  component: PostsImmersiveView,
  meta: { index: 1, title: '文章列表' } // 1级页面索引
},
{
  path: '/posts',
  name: 'posts',
  component: PostListView,
  meta: { index: 10, title: '文章列表' } // 2级页面索引
}
```

**索引规则**:
- 1级页面: 0-9
- 2级页面: 10+

##### 4. 组件通信模式
- **父子通信**: props + emits
- **全局状态**: Pinia store
- **路由状态**: Vue Router 的 reactive route 对象
- **组合式函数**: 逻辑复用和状态共享

### 后端架构

#### 目录结构说明
```
backend/
├── alembic/                 # 数据库迁移管理
│   ├── versions/            # 迁移脚本文件
│   │   └── 34fb55825233_initial_tables.py  # 初始表结构
│   ├── env.py               # 迁移环境配置
│   └── README               # Alembic 使用说明
├── core/                    # 核心配置模块
│   ├── __init__.py          # 包初始化
│   ├── config.py            # 环境变量配置 (Pydantic Settings)
│   ├── database.py          # 数据库连接配置
│   └── security.py          # 安全相关工具 (JWT, 密码哈希)
├── models/                  # 数据模型定义
│   ├── __init__.py          # 包初始化  
│   ├── base.py              # 基础模型类 (包含 id, timestamps)
│   └── blog_models.py       # 博客业务模型 (User, Article, Tag 等)
├── repository/              # 数据访问层 (Repository Pattern)
│   ├── __init__.py          # 包初始化
│   └── auth_repo.py         # 认证相关数据库操作
├── routers/                 # API 路由定义
│   ├── __init__.py          # 包初始化
│   └── v1/                  # v1 版本路由
│       ├── __init__.py      # 包初始化
│       └── api_auth.py      # 认证 API 路由
├── schemas/                 # 数据验证模式 (Pydantic Models)
│   ├── __init__.py          # 包初始化
│   └── user_schema.py       # 用户相关数据模式
├── settings/                # 应用设置 (可能为空或包含额外配置)
│   └── __init__.py          # 包初始化
├── dependencies.py          # 依赖注入函数
├── main.py                  # 应用入口点
└── alembic.ini              # Alembic 配置文件
```

#### 核心组件详解

##### 1. 数据模型设计
在 `models/blog_models.py` 中定义了完整的数据结构：

**用户模型 (User)**:
```python
class User(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)  
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), server_default=UserRole.COMMON.value)
    login_attempts: Mapped[int] = mapped_column(Integer, server_default="0")
    last_fail_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    articles: Mapped[List["Article"]] = relationship(back_populates="author")
```

**关键字段说明**:
- `login_attempts`: 登录失败次数计数
- `last_fail_time`: 最后失败时间戳  
- `role`: 用户角色枚举 (admin/common)

**文章模型 (Article)**:
- 支持发布状态 (published/draft)
- 支持编辑器类型 (markdown/richtext)
- 与标签多对多关联

##### 2. 认证授权系统
**JWT 令牌流程**:
1. 用户登录 → 验证凭据 → 生成 JWT 令牌
2. 后续请求携带令牌 → 验证令牌有效性 → 授权访问

**安全机制**:
- **密码存储**: bcrypt 哈希加密
- **登录锁定**: 连续3次失败锁定15分钟
- **令牌过期**: 可配置的令牌有效期

##### 3. 依赖注入系统
在 `dependencies.py` 中定义可重用的依赖：

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()
```

所有路由通过 `Depends(get_db)` 获取数据库连接。

##### 4. Repository 模式
在 `repository/auth_repo.py` 中封装数据操作：

```python
class AuthRepository:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict):
        """创建新用户"""
        # 密码哈希处理
        hashed_password = get_password_hash(user_data["password"])
        user_data["password"] = hashed_password
        
        # 创建用户实例
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
```

**优势**: 业务逻辑与数据访问分离，便于测试和维护。

## 开发工作流

### 前端开发流程

#### 1. 创建新页面
**步骤1: 创建视图组件**
```vue
<!-- src/views/NewFeatureImmersiveView.vue -->
<template>
  <div class="new-feature-immersive">
    <!-- 1级沉浸式页面内容 -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { useRoute } from 'vue-router'

const route = useRoute()

// 启用滚轮导航
onMounted(() => {
  usePrimaryPageWheel(route.name)
})
</script>
```

**步骤2: 注册路由**
在 `src/router/index.js` 中添加：
```javascript
import NewFeatureImmersiveView from '../views/NewFeatureImmersiveView.vue'

// 在 routes 数组中添加
{
  path: '/new-feature-immersive',
  name: 'new-feature-immersive',
  component: NewFeatureImmersiveView,
  meta: { index: 4, title: '新功能' } // 注意索引顺序
}
```

**步骤3: 更新滚轮导航顺序**
在 `src/composables/usePrimaryPageWheel.js` 中更新 `pageOrder` 数组：
```javascript
const pageOrder = [
  'home',
  'posts-immersive', 
  'about-immersive',
  'message-immersive',
  'new-feature-immersive' // 添加新页面
]
```

#### 2. 创建详情页面
**步骤1: 创建详情组件**
```vue
<!-- src/views/NewFeatureView.vue -->
<template>
  <div class="new-feature-detail">
    <!-- 2级详情页面内容 -->
    <button @click="goBack">返回</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/new-feature-immersive')
}
</script>
```

**步骤2: 注册路由**
```javascript
const NewFeatureView = () => import('../views/NewFeatureView.vue')

{
  path: '/new-feature',
  name: 'new-feature', 
  component: NewFeatureView,
  meta: { index: 40, title: '新功能详情' } // 大索引值
}
```

### 后端开发流程

#### 1. 添加新数据模型
**步骤1: 在 models/blog_models.py 中定义模型**
```python
class NewModel(Base):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    # ... 其他字段
```

**步骤2: 创建数据库迁移**
```bash
alembic revision --autogenerate -m "add_new_model"
alembic upgrade head
```

#### 2. 添加新API路由
**步骤1: 创建 schemas**
在 `schemas/user_schema.py` 或新建 schema 文件：
```python
class NewModelCreate(BaseModel):
    name: str
    description: str

class NewModelOut(BaseModel):
    id: int
    name: str
    description: str
    
    model_config = ConfigDict(from_attributes=True)
```

**步骤2: 创建 repository**
在 `repository/` 目录创建新文件或扩展现有文件：
```python
class NewModelRepository:
    @staticmethod
    async def create_new_model(db: AsyncSession, model_data: dict):
        db_model = NewModel(**model_data)
        db.add(db_model)
        await db.commit()
        await db.refresh(db_model)
        return db_model
```

**步骤3: 创建路由**
在 `routers/v1/` 目录创建新路由文件：
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from schemas.user_schema import NewModelCreate, NewModelOut
from repository.new_model_repo import NewModelRepository

router = APIRouter()

@router.post("/new-models", response_model=NewModelOut)
async def create_new_model(
    model_in: NewModelCreate,
    db: AsyncSession = Depends(get_db)
):
    new_model = await NewModelRepository.create_new_model(db, model_in.model_dump())
    return new_model
```

**步骤4: 注册路由**
在 `main.py` 中注册：
```python
from routers.v1 import api_new_model

app.include_router(api_new_model.router, prefix="/api/v1/new-models", tags=["新功能"])
```

## 代码规范与最佳实践

### 前端规范

#### 1. Vue 3 Composition API 规范
- **setup script**: 使用 `<script setup>` 语法
- **响应式变量**: 使用 `ref`, `reactive`, `computed`
- **生命周期**: 使用 `onMounted`, `onUnmounted` 等
- **Props 定义**: 使用 `defineProps` 明确类型

#### 2. 组合式函数规范
- **命名**: 以 `use` 开头 (`useXXX`)
- **返回值**: 返回需要暴露的状态和方法
- **副作用**: 在函数内部处理副作用逻辑
- **复用性**: 设计为可复用的通用逻辑

#### 3. 样式规范
- **SCSS**: 使用嵌套和变量提高可维护性
- **BEM 命名**: 采用 BEM 命名约定
- **CSS Modules**: 考虑使用 CSS Modules 避免样式冲突

### 后端规范

#### 1. FastAPI 最佳实践
- **类型注解**: 全面使用类型提示
- **Pydantic 模型**: 使用 BaseModel 进行数据验证
- **异步支持**: 全链路异步处理
- **依赖注入**: 使用 Depends 管理依赖

#### 2. SQLAlchemy 2.0 规范
- **Mapped 类型**: 使用 `Mapped[T]` 类型注解
- **关系映射**: 明确定义关系和反向引用
- **会话管理**: 使用上下文管理器确保正确关闭

#### 3. 安全规范
- **密码哈希**: 永远不要存储明文密码
- **输入验证**: 所有输入都要验证
- **错误处理**: 不要泄露敏感信息
- **CORS 配置**: 生产环境严格限制源

## 测试策略

### 前端测试
- **单元测试**: 使用 Vitest 测试组合式函数和组件逻辑
- **组件测试**: 使用 Vue Test Utils 测试组件行为
- **E2E 测试**: 使用 Cypress 或 Playwright 测试用户流程

### 后端测试
- **单元测试**: 使用 pytest 测试 repository 和 utility 函数
- **集成测试**: 测试 API 路由和数据库交互
- **测试数据库**: 使用内存数据库或测试专用数据库

## 部署指南

### 前端部署
```bash
# 构建生产版本
npm run build

# 部署到静态文件服务器 (如 Nginx)
# 将 dist/ 目录内容复制到 Web 服务器根目录
```

### 后端部署
```bash
# 安装生产依赖
pip install -r requirements.txt

# 使用 Gunicorn + Uvicorn 部署
gunicorn -k uvicorn.workers.UvicornWorker main:app

# 或直接使用 Uvicorn (生产环境建议配合进程管理器)
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 环境变量生产配置
```env
# 生产环境 .env 示例
DB_HOST=prod-db-host
DB_PORT=3306  
DB_USER=prod-user
DB_PASSWORD=strong-password
DB_NAME=viteeblog_prod

SECRET_KEY=very-strong-secret-key-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS 生产配置 (在代码中修改)
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## 故障排除

### 常见问题

#### 1. 滚轮导航不工作
- **检查**: 页面是否正确注册到 `pageOrder` 数组
- **检查**: 路由 `meta.index` 是否为正确的 1级页面索引
- **检查**: 组件是否正确调用 `usePrimaryPageWheel`

#### 2. 数据库连接失败
- **检查**: `.env` 文件中的数据库配置是否正确
- **检查**: MySQL 服务是否正在运行
- **检查**: 数据库用户是否有足够权限

#### 3. CORS 错误
- **开发环境**: 确保后端 CORS 配置允许前端端口
- **生产环境**: 确保前端域名在允许的源列表中

### 调试技巧

#### 前端调试
- **Vue DevTools**: 安装浏览器扩展进行组件调试
- **Console Logging**: 在组合式函数中添加日志
- **Network Tab**: 检查 API 请求和响应

#### 后端调试
- **FastAPI Docs**: 使用自动生成的文档测试 API
- **Database Logs**: 启用 SQLAlchemy echo 查看 SQL 查询
- **Debug Mode**: 在开发环境中启用详细日志

## 未来开发路线图

### 短期任务 (1-2周)
1. **完善文章管理**: 实现文章的 CRUD 操作
2. **评论系统**: 添加文章评论功能
3. **用户个人中心**: 允许用户管理个人信息

### 中期任务 (1个月)
1. **搜索功能**: 实现全文搜索
2. **标签系统**: 完善标签管理和筛选
3. **SEO 优化**: 添加 meta 标签和 sitemap

### 长期任务 (3个月+)
1. **统计分析**: 集成访问统计
2. **通知系统**: 实现消息通知
3. **移动端优化**: 响应式设计改进
4. **性能监控**: 集成 APM 工具

## 贡献指南

### 代码提交规范
- **分支策略**: feature/xxx, bugfix/xxx
- **提交信息**: 遵循 conventional commits 规范
- **代码审查**: 所有更改都需要 PR 审查

### 开发流程
1. Fork 仓库
2. 创建特性分支
3. 实现功能/修复 bug
4. 编写测试 (如果适用)
5. 提交 PR
6. 等待审查和合并

---

**注意**: 本文档假设你已经具备 Vue 3、FastAPI 和基本的 Web 开发知识。如果遇到任何不清楚的地方，请参考官方文档或在项目 issue 中提问。

# ViteeBlog 前端项目说明文档

## 1. 项目概述

ViteeBlog 是一个现代化的博客系统前端，采用 Vue 3 + Vite 技术栈构建，具有以下核心特性：

- **沉浸式用户体验**：支持首页、文章、关于、留言等页面的沉浸式浏览体验
- **流畅的页面过渡动画**：基于 CSS 动画和 JavaScript 控制的页面切换效果
- **响应式滚轮导航**：在主要页面间通过鼠标滚轮实现无缝导航
- **模块化架构**：采用 Vue 3 Composition API 和组件化设计模式

## 2. 技术栈

### 核心依赖
- **Vue 3.5.30** - 渐进式 JavaScript 框架
- **Vue Router 4.6.4** - 官方路由管理器
- **Pinia 3.0.4** - 状态管理库（当前未使用但已配置）
- **Sass 1.98.0** - CSS 预处理器

### 开发工具
- **Vite 8.0.1** - 下一代前端构建工具
- **@vitejs/plugin-vue** - Vite 的 Vue 插件

## 3. 项目结构

```
frontend/
├── layout/                    # 布局组件（重复目录，实际使用 src/layout）
├── src/
│   ├── assets/                # 静态资源文件
│   │   ├── main.scss          # 全局基础样式
│   │   ├── avatar.png         # 用户头像
│   │   └── hero-bg.jpg        # 首页背景图
│   ├── components/            # 可复用组件
│   │   ├── Navbar.vue         # 固定导航栏组件
│   │   ├── PostItem.vue       # 单篇文章展示组件
│   │   └── PostList.vue       # 文章列表组件
│   ├── composables/           # 组合式函数（逻辑复用）
│   │   ├── usePageTransition.js    # 页面过渡动画逻辑
│   │   └── usePrimaryPageWheel.js  # 主要页面滚轮导航逻辑
│   ├── layout/                # 布局组件
│   │   └── FrontLayout.vue    # 前端布局（未在main.js中使用）
│   ├── router/                # 路由配置
│   │   └── index.js           # 路由定义和全局守卫
│   ├── views/                 # 页面视图组件
│   │   ├── HomeView.vue               # 首页（沉浸式）
│   │   ├── PostListView.vue           # 文章列表页（常规）
│   │   ├── PostsImmersiveView.vue     # 文章沉浸式页面
│   │   ├── AboutView.vue              # 关于页面（常规）
│   │   ├── AboutImmersiveView.vue     # 关于沉浸式页面
│   │   ├── MessageView.vue            # 留言页面（常规）
│   │   ├── MessageImmersiveView.vue   # 留言沉浸式页面
│   │   └── LoginView.vue              # 登录页面
│   ├── App.vue                # 根组件
│   ├── main.js                # 应用入口文件
│   └── style.css              # 全局CSS样式
├── index.html                 # HTML模板
├── package.json               # 项目依赖和脚本配置
├── package-lock.json          # 依赖锁定文件
└── vite.config.js             # Vite构建配置
```

## 4. 核心功能特性

### 4.1 双模式页面设计

项目采用独特的双模式页面设计：

- **沉浸式页面** (`*-immersive`): 
  - 路径: `/`, `/posts-immersive`, `/about-immersive`, `/message-immersive`, `/login`
  - 特点: 透明导航栏、毛玻璃效果、无顶部内边距
  - 适用于首页和主要导航页面

- **常规页面** (`*`):
  - 路径: `/posts`, `/about`, `/message`
  - 特点: 白色背景导航栏、内容区域有顶部内边距(90px)
  - 适用于详细内容展示页面

### 4.2 页面过渡动画系统

通过 `usePageTransition.js` 实现智能页面切换动画：

- **前进动画**: 新页面从右侧切入，旧页面向左微移并变暗
- **后退动画**: 新页面从左侧淡入，旧页面向右侧擦除消失
- **路由索引控制**: 通过 `meta.index` 属性判断页面层级关系
- **动画状态管理**: 防止连续快速切换导致的动画冲突

### 4.3 滚轮导航系统

在主要沉浸式页面中实现滚轮导航：

- **支持页面**: 首页 → 文章 → 关于 → 留言
- **向上滚动**: 返回上一个页面
- **向下滚动**: 进入下一个页面
- **防抖处理**: 动画进行中时禁用滚轮导航

### 4.4 动态导航栏

`Navbar.vue` 组件提供智能导航体验：

- **沉浸模式**: 透明背景 + 毛玻璃效果 + 白色文字
- **常规模式**: 白色背景 + 黑色文字 + 底部边框
- **动态模糊层**: 使用 `backdrop-filter` 实现磨砂玻璃质感
- **路由高亮**: 当前页面在导航项下方显示小圆点指示器

## 5. 路由配置

### 路由映射表

| 路径 | 名称 | 组件 | 模式 | 索引 |
|------|------|------|------|------|
| `/` | home | HomeView | 沉浸式 | 0 |
| `/posts-immersive` | posts-immersive | PostsImmersiveView | 沉浸式 | 1 |
| `/posts` | posts | PostListView | 常规 | 10 |
| `/about-immersive` | about-immersive | AboutImmersiveView | 沉浸式 | 2 |
| `/about` | about | AboutView | 常规 | 20 |
| `/message-immersive` | message-immersive | MessageImmersiveView | 沉浸式 | 3 |
| `/message` | message | MessageView | 常规 | 30 |
| `/login` | login | LoginView | 沉浸式 | 4 |

### 路由特性
- **动态标题**: 通过全局后置守卫自动设置页面标题
- **滚动行为**: 切换页面时自动回到顶部
- **懒加载**: 常规页面采用动态导入提高初始加载性能

## 6. 开发脚本

### package.json scripts

```json
{
  "scripts": {
    "dev": "vite",           // 开发服务器
    "build": "vite build",   // 生产构建
    "preview": "vite preview" // 本地预览构建结果
  }
}
```

### 构建配置 (vite.config.js)

- **路径别名**: `@` 指向 `src` 目录
- **Vue插件**: 启用 Vue 3 支持
- **ES模块**: 使用原生 ES 模块系统

## 7. 样式系统

### 全局样式变量
项目使用 CSS 自定义属性（CSS Variables）管理主题：

- `--bg-white`: 白色背景
- `--text-main`: 主要文字颜色

### SCSS 特性
- **嵌套规则**: 提高样式可读性
- **混合宏**: 复用样式逻辑
- **作用域样式**: 使用 `scoped` 属性避免样式冲突

### 特殊效果
- **毛玻璃效果**: `backdrop-filter: blur(30px) saturate(180%) brightness(0.85)`
- **渐变文字**: `-webkit-background-clip: text`
- **遮罩渐变**: `mask-image` 实现边缘消融效果

## 8. 应用初始化流程

1. **入口文件**: `src/main.js`
   - 创建 Vue 应用实例
   - 注册 Vue Router
   - 挂载到 `#app` 元素

2. **根组件**: `App.vue`
   - 引入导航栏组件
   - 配置路由视图过渡动画
   - 计算当前页面是否为沉浸式模式

3. **路由系统**: `router/index.js`
   - 定义所有路由规则
   - 配置页面元数据（索引、标题）
   - 设置全局导航守卫

## 9. 性能优化策略

### 代码分割
- **静态导入**: 核心页面组件（提高关键路径加载速度）
- **动态导入**: 非核心页面组件（减少初始包体积）

### 动画优化
- **CSS硬件加速**: 使用 `transform` 和 `opacity` 属性
- **防抖处理**: 避免动画冲突和性能问题
- **z-index管理**: 确保正确的图层叠放顺序

### 资源优化
- **图片优化**: 头像和背景图经过适当压缩
- **字体加载**: 使用系统字体避免额外网络请求

## 10. 扩展建议

### 当前限制
- 缺少 Pinia 状态管理的实际应用
- 文章数据目前为静态模拟数据
- 缺少 API 集成和真实数据获取

### 改进建议
1. **API集成**: 添加 Axios 或 Fetch API 调用后端接口
2. **状态管理**: 使用 Pinia 管理用户状态、文章数据等
3. **响应式优化**: 添加移动端适配和触摸事件支持
4. **SEO优化**: 考虑服务端渲染(SSR)或预渲染方案
5. **PWA支持**: 添加离线缓存和推送通知功能

## 11. 开发环境要求

- **Node.js**: v16+ (推荐 LTS 版本)
- **包管理器**: npm, yarn 或 pnpm
- **浏览器**: 现代浏览器（Chrome, Firefox, Safari 最新版）
- **开发工具**: VS Code 推荐安装 Volar 插件

## 12. 快速开始

```bash
# 安装依赖
cd frontend
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

访问 `http://localhost:5173` 查看应用（默认 Vite 端口）。
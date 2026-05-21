<template>
  <!-- Pages: 整个应用就是一个展示页面 -->
     <div class="demo-container">
        <!-- 导航栏 -->
        <div class="navbar">
            <div class="logo">⚛️ Atomic Design</div>
            <div class="nav-links">
                <a href="#">首页</a>
                <a href="#">组件</a>
                <a href="#">文档</a>
                <a href="#">关于</a>
            </div>
            <div class="nav-actions">
                <button class="btn btn-text">登录</button>
                <button class="btn btn-primary">注册</button>
            </div>
        </div>
        
        <!-- ==================== 原子层演示 ==================== -->
        <div class="section">
            <h1 class="section-title">🎨 原子层 (Atoms)</h1>
            
            <div class="subsection-title">颜色原子 - 8色系统</div>
            <div class="color-grid">
                <div class="color-swatch"><div class="color-box primary"></div><div class="color-label">#53b0ff</div></div>
                <div class="color-swatch"><div class="color-box primary-deep"></div><div class="color-label">#000eff</div></div>
                <div class="color-swatch"><div class="color-box secondary"></div><div class="color-label">#7200ff</div></div>
                <div class="color-swatch"><div class="color-box accent"></div><div class="color-label">#f86eff</div></div>
                <div class="color-swatch"><div class="color-box warning"></div><div class="color-label">#ffec7b</div></div>
                <div class="color-swatch"><div class="color-box success"></div><div class="color-label">#51ffd6</div></div>
                <div class="color-swatch"><div class="color-box error"></div><div class="color-label">#ff0072</div></div>
            </div>
            
            <div class="subsection-title">文字原子</div>
            <div class="card">
                <div class="text-h1">标题一 (H1) - 32px</div>
                <div class="text-h2">标题二 (H2) - 24px</div>
                <div class="text-h3">标题三 (H3) - 20px</div>
                <div class="text-body">正文文字 - 16px，用于主要内容展示，阅读舒适。</div>
                <div class="text-caption">辅助文字 - 13px，用于说明性内容</div>
                <div class="text-small">最小文字 - 11px，用于角标、时间戳等</div>
            </div>
            
            <div class="subsection-title">按钮原子</div>
            <div class="demo-row">
                <button class="btn btn-primary">主要按钮</button>
                <button class="btn btn-secondary">次要按钮</button>
                <button class="btn btn-success">成功按钮</button>
                <button class="btn btn-warning">警告按钮</button>
                <button class="btn btn-error">错误按钮</button>
                <button class="btn btn-outline">边框按钮</button>
                <button class="btn btn-text">文字按钮</button>
            </div>
            
            <div class="subsection-title">输入框原子</div>
            <div class="demo-row">
                <input class="input" type="text" placeholder="默认输入框">
                <input class="input" type="text" placeholder="禁用状态" disabled>
            </div>
            
            <div class="subsection-title">标签原子</div>
            <div class="demo-row">
                <span class="tag tag-primary">主要标签</span>
                <span class="tag tag-success">成功标签</span>
                <span class="tag tag-warning">黄色高亮</span>
                <span class="tag tag-error">错误标签</span>
            </div>
            
            <div class="subsection-title">图标原子（黄色专用）</div>
            <div class="demo-row">
                <span class="icon-star">⭐</span>
                <span class="icon-star">★</span>
                <span class="icon-success">✓</span>
                <span class="icon-error">✗</span>
            </div>
        </div>
        
        <!-- ==================== 分子层演示 ==================== -->
        <div class="section">
            <h1 class="section-title">🧩 分子层 (Molecules)</h1>
            
            <div class="subsection-title">搜索框分子</div>
            <div class="search-box">
                <input class="search-input" type="text" placeholder="搜索...">
                <button class="search-btn">搜索</button>
            </div>
            
            <div class="subsection-title">用户卡片分子</div>
            <div class="user-card">
                <div class="avatar"></div>
                <div class="info">
                    <div class="name">张三</div>
                    <div class="role">产品设计师</div>
                </div>
                <button class="action-btn">关注</button>
            </div>
            
            <div class="subsection-title">评分分子（黄色星星）</div>
            <div class="rating">
                <div class="stars">
                    <span class="star active">★</span>
                    <span class="star active">★</span>
                    <span class="star active">★</span>
                    <span class="star active">★</span>
                    <span class="star">★</span>
                </div>
                <span class="rating-value">4.0 分 (128 评价)</span>
            </div>
            
            <div class="subsection-title">菜单项分子</div>
            <div style="max-width: 260px;">
                <div class="menu-item active">
                    <span class="menu-icon">🏠</span>
                    <span class="menu-text">首页</span>
                </div>
                <div class="menu-item">
                    <span class="menu-icon">👤</span>
                    <span class="menu-text">个人资料</span>
                </div>
                <div class="menu-item">
                    <span class="menu-icon">⚙️</span>
                    <span class="menu-text">设置</span>
                </div>
            </div>
        </div>
        
        <!-- ==================== 组织层演示 ==================== -->
        <div class="section">
            <h1 class="section-title">🏗️ 组织层 (Organisms)</h1>
            
            <div class="subsection-title">文章列表组织</div>
            <div class="article-list">
                <div class="article-item">
                    <div class="title">原子设计系统实战指南</div>
                    <div class="meta">
                        <span>作者: 李明</span>
                        <span>2024-01-15</span>
                        <span>阅读 2.3k</span>
                    </div>
                    <div class="summary">原子设计是一种构建UI系统的方法论，从最小的原子组件开始，逐步组合成分子、组织、模板和页面...</div>
                </div>
                <div class="article-item">
                    <div class="title">暗色模式设计最佳实践</div>
                    <div class="meta">
                        <span>作者: 王芳</span>
                        <span>2024-01-10</span>
                        <span>阅读 1.8k</span>
                    </div>
                    <div class="summary">暗色模式不仅仅是把背景变成黑色，还需要考虑对比度、色彩层次和用户舒适度...</div>
                </div>
                <div class="article-item">
                    <div class="title">设计系统的可维护性思考</div>
                    <div class="meta">
                        <span>作者: 赵雷</span>
                        <span>2024-01-05</span>
                        <span>阅读 1.2k</span>
                    </div>
                    <div class="summary">一个好的设计系统应该在保证一致性的同时，也具备足够的灵活性和扩展性...</div>
                </div>
            </div>
            
            <div class="subsection-title">表单组</div>
            <div class="form-group">
                <label>用户名</label>
                <input type="text" placeholder="请输入用户名">
                <div class="helper-text">用户名长度4-20个字符</div>
            </div>
            <div class="form-group">
                <label>邮箱</label>
                <input type="email" placeholder="example@email.com">
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" placeholder="请输入密码">
                <div class="error-text">密码长度至少8位</div>
            </div>
        </div>
        
        <!-- ==================== 模板层演示 ==================== -->
        <div class="section">
            <h1 class="section-title">📐 模板层 (Templates)</h1>
            
            <div class="subsection-title">双栏布局模板</div>
            <div class="layout-two-column" style="min-height: auto; border: 1px solid var(--border-default); border-radius: var(--radius-lg); margin-bottom: 20px;">
                <div class="sidebar">
                    <div class="menu-item active"><span class="menu-icon">📊</span><span class="menu-text">仪表盘</span></div>
                    <div class="menu-item"><span class="menu-icon">👥</span><span class="menu-text">用户管理</span></div>
                    <div class="menu-item"><span class="menu-icon">📝</span><span class="menu-text">内容管理</span></div>
                    <div class="menu-item"><span class="menu-icon">⚙️</span><span class="menu-text">系统设置</span></div>
                </div>
                <div class="main-content">
                    <div class="card" style="margin-bottom: 16px;">
                        <div class="text-h3">欢迎回来，张三</div>
                        <div class="text-caption">这是你的仪表盘概览</div>
                    </div>
                    <div class="layout-grid">
                        <div class="card">卡片内容 1</div>
                        <div class="card">卡片内容 2</div>
                        <div class="card">卡片内容 3</div>
                    </div>
                </div>
            </div>
            
            <div class="subsection-title">网格布局模板</div>
            <div class="layout-grid">
                <div class="card">
                    <div class="text-h3">项目一</div>
                    <div class="text-caption">这是一个项目卡片</div>
                </div>
                <div class="card">
                    <div class="text-h3">项目二</div>
                    <div class="text-caption">这是一个项目卡片</div>
                </div>
                <div class="card">
                    <div class="text-h3">项目三</div>
                    <div class="text-caption">这是一个项目卡片</div>
                </div>
            </div>
        </div>
        
        <!-- ==================== 页面层演示 ==================== -->
        <div class="section">
            <h1 class="section-title">📄 页面层 (Pages)</h1>
            
            <div class="subsection-title">仪表盘页面</div>
            <div class="dashboard-page" style="background: var(--bg-surface); border-radius: var(--radius-lg); margin-bottom: 24px; padding: 24px;">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">1,234</div>
                        <div class="stat-label">总用户数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">¥ 12,345</div>
                        <div class="stat-label">总收入</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">89%</div>
                        <div class="stat-label">满意度</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">24</div>
                        <div class="stat-label">进行中</div>
                    </div>
                </div>
                <div class="recent-list">
                    <div class="list-header">
                        <span class="text-h3">最近活动</span>
                        <button class="btn btn-text">查看全部 →</button>
                    </div>
                    <div class="article-list">
                        <div class="article-item"><div class="title">用户评论了你的文章</div><div class="meta">5分钟前</div></div>
                        <div class="article-item"><div class="title">新用户注册</div><div class="meta">1小时前</div></div>
                        <div class="article-item"><div class="title">系统更新完成</div><div class="meta">3小时前</div></div>
                    </div>
                </div>
            </div>
            
            <div class="subsection-title">个人资料页面</div>
            <div class="profile-page" style="background: var(--bg-surface); border-radius: var(--radius-lg); margin-bottom: 24px;">
                <div class="profile-header">
                    <div class="avatar-lg"></div>
                    <div class="username">张三</div>
                    <div class="text-caption">产品设计师 · 北京</div>
                </div>
                <div class="profile-form">
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" value="zhangsan">
                    </div>
                    <div class="form-group">
                        <label>邮箱</label>
                        <input type="email" value="zhangsan@example.com">
                    </div>
                    <div class="form-group">
                        <label>个人简介</label>
                        <textarea rows="3" placeholder="介绍一下你自己..."></textarea>
                    </div>
                    <div class="flex gap-2">
                        <button class="btn btn-primary">保存修改</button>
                        <button class="btn btn-outline">取消</button>
                    </div>
                </div>
            </div>
            
            <div class="subsection-title">设置页面</div>
            <div class="settings-page" style="background: var(--bg-surface); border-radius: var(--radius-lg);">
                <div class="settings-section">
                    <div class="section-title">通知设置</div>
                    <div class="flex justify-between" style="padding: 12px 0;">
                        <span>邮件通知</span>
                        <span>✓</span>
                    </div>
                    <div class="flex justify-between" style="padding: 12px 0; border-top: 1px solid var(--border-default);">
                        <span>推送通知</span>
                        <span>✓</span>
                    </div>
                </div>
                <div class="settings-section">
                    <div class="section-title">隐私设置</div>
                    <div class="flex justify-between" style="padding: 12px 0;">
                        <span>公开资料</span>
                        <span>✓</span>
                    </div>
                    <div class="flex justify-between" style="padding: 12px 0; border-top: 1px solid var(--border-default);">
                        <span>显示在线状态</span>
                        <span>✗</span>
                    </div>
                </div>
                <button class="btn btn-error w-full">注销账号</button>
            </div>
        </div>
        
        <!-- 设计系统总结 -->
        <div class="card" style="text-align: center; margin-top: 48px; margin-bottom: 48px;">
            <div class="text-h2" style="margin-bottom: 16px;">⚛️ 原子设计系统</div>
            <div class="text-body" style="color: var(--text-secondary); margin-bottom: 24px;">
                从原子 → 分子 → 组织 → 模板 → 页面<br>
                8色系统 | 暗色主题 | 扁平化设计
            </div>
            <div class="flex justify-center gap-2">
                <button class="btn btn-primary">开始使用</button>
                <button class="btn btn-outline">查看文档</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'AtomicDesignDemo',
  data() {
    return {
      searchText: '',
      currentPage: 'home',
      pageNames: {
        home: '首页 (Home)',
        detail: '详情页 (Detail)',
        user: '个人中心 (User Center)'
      }
    };
  }
};
</script>

<style lang="scss" scoped>
/* ==================== 设计令牌 (Design Tokens) - 暗色8色系统 ==================== */
// 品牌色（你的8色）
$primary-color: #53b0ff;      // 主色（浅蓝）
$primary-deep: #000eff;       // 深蓝
$secondary-color: #7200ff;    // 辅色（紫）
$accent-color: #f86eff;       // 粉红（强调）
$warning-color: #ffec7b;      // 黄色（高亮/注意）
$success-color: #51ffd6;      // 青绿（成功）
$error-color: #ff0072;        // 品红（错误）

// 语义色别名
$text-link: $primary-color;

// 背景层（纯扁平，无渐变）
$bg-base: #000000;            // 主背景
$bg-surface: #0f0f0f;         // 卡片/面板
$bg-elevated: #1a1a1a;        // 弹窗/抽屉
$bg-hover: #1f1f1f;           // 悬浮态

// 文字（纯扁平，用固定色值）
$text-primary: #ffffff;
$text-secondary: #a0a0a0;
$text-tertiary: #6b6b6b;
$text-disabled: #4a4a4a;

// 边框（扁平，无阴影）
$border-default: #2a2a2a;
$border-light: #3a3a3a;

// 阴影（扁平化，只用极简阴影）
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
$shadow-md: 0 2px 4px rgba(0, 0, 0, 0.2);
$shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.2);

// 圆角
$radius-sm: 4px;
$radius-md: 8px;
$radius-lg: 12px;
$radius-xl: 16px;

/* ==================== 全局重置 ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: $bg-base;
  color: $text-primary;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}

/* ==================== Atoms (原子层) ==================== */
// 颜色原子展示
.color-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.color-swatch {
  width: 80px;
  text-align: center;
  
  .color-box {
    width: 80px;
    height: 80px;
    border-radius: $radius-md;
    margin-bottom: 8px;
    
    &.primary { background: $primary-color; }
    &.primary-deep { background: $primary-deep; }
    &.secondary { background: $secondary-color; }
    &.accent { background: $accent-color; }
    &.warning { background: $warning-color; }
    &.success { background: $success-color; }
    &.error { background: $error-color; }
  }
  
  .color-label {
    font-size: 11px;
    color: $text-tertiary;
    font-family: monospace;
  }
}

// 文字原子
.text-h1 { font-size: 32px; font-weight: 700; line-height: 1.2; margin: 8px 0; }
.text-h2 { font-size: 24px; font-weight: 600; line-height: 1.3; margin: 8px 0; }
.text-h3 { font-size: 20px; font-weight: 600; line-height: 1.4; margin: 8px 0; }
.text-body { font-size: 16px; line-height: 1.5; margin: 4px 0; }
.text-caption { font-size: 13px; color: $text-secondary; margin: 4px 0; }
.text-small { font-size: 11px; color: $text-tertiary; }

// 按钮原子
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.15s ease;
  
  &:hover { opacity: 0.85; }
  &:active { transform: scale(0.98); }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}

.btn-primary {
  background: $primary-color;
  color: #000000;
}
.btn-secondary {
  background: $secondary-color;
  color: #ffffff;
}
.btn-success {
  background: $success-color;
  color: #000000;
}
.btn-warning {
  background: $warning-color;
  color: #000000;
}
.btn-error {
  background: $error-color;
  color: #ffffff;
}
.btn-outline {
  background: transparent;
  border: 1px solid $border-default;
  color: $text-primary;
  
  &:hover { background: $bg-hover; }
}
.btn-text {
  background: transparent;
  color: $primary-color;
  
  &:hover { background: rgba($primary-color, 0.1); }
}

// 输入框原子
.input {
  padding: 10px 14px;
  background: $bg-surface;
  border: 1px solid $border-default;
  border-radius: $radius-md;
  color: $text-primary;
  font-size: 14px;
  transition: all 0.15s ease;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
  
  &::placeholder {
    color: $text-tertiary;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 卡片原子
.card {
  background: $bg-surface;
  border: 1px solid $border-default;
  border-radius: $radius-lg;
  padding: 20px;
}

// 标签原子
.tag {
  display: inline-block;
  padding: 4px 10px;
  font-size: 12px;
  border-radius: $radius-sm;
  font-weight: 500;
  
  &.tag-primary { background: rgba($primary-color, 0.15); color: $primary-color; }
  &.tag-success { background: rgba($success-color, 0.15); color: $success-color; }
  &.tag-warning { background: rgba($warning-color, 0.15); color: $warning-color; }
  &.tag-error { background: rgba($error-color, 0.15); color: $error-color; }
}

// 图标原子（黄色专门用于星星等）
.icon-star {
  color: $warning-color;
  font-size: 20px;
}
.icon-success {
  color: $success-color;
  font-size: 20px;
}
.icon-error {
  color: $error-color;
  font-size: 20px;
}

/* ==================== Molecules (分子层) ==================== */
// 搜索框分子
.search-box {
  display: flex;
  gap: 8px;
  
  .search-input {
    flex: 1;
    padding: 10px 14px;
    background: $bg-surface;
    border: 1px solid $border-default;
    border-radius: $radius-md;
    color: $text-primary;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
  }
  
  .search-btn {
    @extend .btn-primary;
    padding: 8px 20px;
  }
}

// 用户卡片分子
.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: $bg-surface;
  border: 1px solid $border-default;
  border-radius: $radius-lg;
  
  .avatar {
    width: 48px;
    height: 48px;
    background: $secondary-color;
    border-radius: 50%;
    flex-shrink: 0;
  }
  
  .info {
    flex: 1;
    
    .name {
      font-weight: 600;
      margin-bottom: 4px;
    }
    
    .role {
      font-size: 13px;
      color: $text-secondary;
    }
  }
  
  .action-btn {
    @extend .btn-outline;
    padding: 6px 16px;
    font-size: 13px;
  }
}

// 评分分子（黄色星星专用）
.rating {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .stars {
    display: flex;
    gap: 4px;
    
    .star {
      color: $text-tertiary;
      font-size: 20px;
      cursor: pointer;
      
      &.active {
        color: $warning-color;
      }
      
      &:hover {
        color: $warning-color;
      }
    }
  }
  
  .rating-value {
    font-size: 14px;
    color: $text-secondary;
  }
}

// 菜单项分子
.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: $radius-md;
  cursor: pointer;
  transition: background 0.15s;
  
  &:hover {
    background: $bg-hover;
  }
  
  &.active {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
  
  .menu-icon {
    width: 20px;
    font-size: 18px;
  }
  
  .menu-text {
    flex: 1;
    font-size: 14px;
  }
}

/* ==================== Organisms (组织层) ==================== */
// 导航栏
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: $bg-surface;
  border-bottom: 1px solid $border-default;
  
  .logo {
    font-size: 20px;
    font-weight: 700;
    color: $primary-color;
  }
  
  .nav-links {
    display: flex;
    gap: 24px;
    
    a {
      color: $text-secondary;
      text-decoration: none;
      font-size: 14px;
      
      &:hover {
        color: $primary-color;
      }
    }
  }
  
  .nav-actions {
    display: flex;
    gap: 12px;
  }
}

// 侧边栏
.sidebar {
  width: 260px;
  background: $bg-surface;
  border-right: 1px solid $border-default;
  padding: 16px 0;
}

// 文章列表
.article-list {
  .article-item {
    padding: 16px;
    border-bottom: 1px solid $border-default;
    
    &:hover {
      background: $bg-hover;
    }
    
    .title {
      font-weight: 600;
      margin-bottom: 8px;
    }
    
    .meta {
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: $text-tertiary;
      margin-bottom: 8px;
    }
    
    .summary {
      font-size: 14px;
      color: $text-secondary;
    }
  }
}

// 表单组
.form-group {
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
  }
  
  input, textarea, select {
    width: 100%;
    padding: 10px 14px;
    background: $bg-surface;
    border: 1px solid $border-default;
    border-radius: $radius-md;
    color: $text-primary;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
  }
  
  .helper-text {
    margin-top: 6px;
    font-size: 12px;
    color: $text-tertiary;
  }
  
  .error-text {
    margin-top: 6px;
    font-size: 12px;
    color: $error-color;
  }
}

/* ==================== Templates (模板层) ==================== */
// 双栏模板
.layout-two-column {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  
  .main-content {
    padding: 24px;
  }
}

// 网格模板
.layout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

// 列表模板
.layout-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ==================== 页面示例 ==================== */
// 仪表盘页面
.dashboard-page {
  padding: 24px;
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
    
    .stat-card {
      @extend .card;
      text-align: center;
      
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: $primary-color;
      }
      
      .stat-label {
        font-size: 13px;
        color: $text-secondary;
        margin-top: 8px;
      }
    }
  }
  
  .recent-list {
    @extend .card;
    
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid $border-default;
    }
  }
}

// 个人资料页面
.profile-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
  
  .profile-header {
    text-align: center;
    margin-bottom: 32px;
    
    .avatar-lg {
      width: 100px;
      height: 100px;
      background: $secondary-color;
      border-radius: 50%;
      margin: 0 auto 16px;
    }
    
    .username {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 8px;
    }
  }
  
  .profile-form {
    @extend .card;
  }
}

// 设置页面
.settings-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 32px 24px;
  
  .settings-section {
    @extend .card;
    margin-bottom: 24px;
    
    .section-title {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid $border-default;
    }
  }
}

/* ==================== 响应式工具 ==================== */
.hide-mobile {
  @media (max-width: 768px) {
    display: none;
  }
}

.show-mobile {
  display: none;
  @media (max-width: 768px) {
    display: block;
  }
}

.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 8px; }
.gap-4 { gap: 16px; }
.mt-4 { margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.p-4 { padding: 16px; }
.w-full { width: 100%; }
</style>
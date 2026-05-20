<template>
  <!-- Pages: 整个应用就是一个展示页面 -->
  <div class="demo-page">
    <!-- Templates: 页面布局模板 -->
    <div class="demo-template">
      <div class="page-header">
        <h1 class="page-title">🎨 原子设计系统 (Atomic Design System)</h1>
        <p class="page-subtitle">完整展示 Atoms → Molecules → Organisms → Templates → Pages 五层架构</p>
      </div>

      <!-- Organisms: 层级展示组织 -->
      <div class="hierarchy-organism">

        <!-- Level 1: Atoms 展示区 -->
        <div class="level-section">
          <div class="level-badge">✨ Level 1: Atoms (原子)</div>
          <p class="level-desc">最小的UI单元，不可再分的基础组件</p>
          <div class="atoms-showcase">
            <div class="atom-card">
              <div class="atom-label">颜色原子</div>
              <div class="color-demo">
                <div class="color-box primary"></div>
                <div class="color-box success"></div>
                <div class="color-box warning"></div>
                <div class="color-box error"></div>
              </div>
            </div>
            <div class="atom-card">
              <div class="atom-label">文字原子</div>
              <div class="text-demo">
                <div class="text-h1">H1标题</div>
                <div class="text-h2">H2标题</div>
                <div class="text-body">正文内容</div>
                <div class="text-caption">辅助说明</div>
              </div>
            </div>
            <div class="atom-card">
              <div class="atom-label">按钮原子</div>
              <div class="button-demo">
                <button class="btn-primary">主要按钮</button>
                <button class="btn-default">默认按钮</button>
                <button class="btn-text">文字按钮</button>
              </div>
            </div>
            <div class="atom-card">
              <div class="atom-label">输入原子</div>
              <div class="input-demo">
                <input type="text" placeholder="文本输入框" class="input-base" />
                <input type="text" placeholder="禁用状态" class="input-base" disabled />
              </div>
            </div>
            <div class="atom-card">
              <div class="atom-label">间距原子</div>
              <div class="spacing-demo">
                <div class="spacing-item xs">xs</div>
                <div class="spacing-item sm">sm</div>
                <div class="spacing-item md">md</div>
                <div class="spacing-item lg">lg</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 层级连接箭头 -->
        <div class="level-arrow">▼ Atoms 组合成 Molecules ▼</div>

        <!-- Level 2: Molecules 展示区 -->
        <div class="level-section">
          <div class="level-badge">🔬 Level 2: Molecules (分子)</div>
          <p class="level-desc">由多个原子组合而成的相对复杂组件</p>
          <div class="molecules-showcase">
            <div class="molecule-card">
              <div class="molecule-title">🔍 搜索框分子</div>
              <div class="search-molecule">
                <input type="text" placeholder="搜索..." class="search-input" v-model="searchText" />
                <button class="search-btn">搜索</button>
              </div>
              <div class="molecule-composition">
                <span class="badge-atom">Input原子</span> +
                <span class="badge-atom">Button原子</span>
              </div>
            </div>
            <div class="molecule-card">
              <div class="molecule-title">👤 用户卡片分子</div>
              <div class="user-card-molecule">
                <div class="user-avatar"></div>
                <div class="user-info">
                  <div class="user-name">张三</div>
                  <div class="user-role">前端工程师</div>
                </div>
                <button class="follow-btn">+ 关注</button>
              </div>
              <div class="molecule-composition">
                <span class="badge-atom">Avatar原子</span> +
                <span class="badge-atom">Text原子</span> +
                <span class="badge-atom">Button原子</span>
              </div>
            </div>
            <div class="molecule-card">
              <div class="molecule-title">⭐ 评分组件分子</div>
              <div class="rating-molecule">
                <span class="star" v-for="n in 5" :key="n">★</span>
                <span class="rating-text">4.5分 (128人评价)</span>
              </div>
              <div class="molecule-composition">
                <span class="badge-atom">Icon原子</span> +
                <span class="badge-atom">Text原子</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 层级连接箭头 -->
        <div class="level-arrow">▼ Molecules 组合成 Organisms ▼</div>

        <!-- Level 3: Organisms 展示区 -->
        <div class="level-section">
          <div class="level-badge">🧬 Level 3: Organisms (组织)</div>
          <p class="level-desc">由分子、原子组合而成的独立功能区块</p>
          <div class="organisms-showcase">
            <div class="organism-card">
              <div class="organism-title">📋 导航栏组织</div>
              <div class="navbar-organism">
                <div class="logo">Logo</div>
                <div class="nav-links">
                  <a href="#" class="nav-link">首页</a>
                  <a href="#" class="nav-link">产品</a>
                  <a href="#" class="nav-link">关于</a>
                </div>
                <div class="search-molecule-mini">
                  <input type="text" placeholder="搜索..." />
                </div>
              </div>
              <div class="organism-composition">
                包含: 搜索分子 + 导航链接分子 + Logo原子
              </div>
            </div>
            <div class="organism-card">
              <div class="organism-title">📰 文章列表组织</div>
              <div class="article-list-organism">
                <div v-for="i in 3" :key="i" class="article-item">
                  <div class="article-title">文章标题 {{ i }}</div>
                  <div class="article-meta">2024-01-15 • 1.2k阅读</div>
                  <div class="article-summary">这是文章的摘要内容，展示文章的核心信息...</div>
                </div>
              </div>
              <div class="organism-composition">
                包含: 文章卡片分子 × N + 分页分子
              </div>
            </div>
            <div class="organism-card">
              <div class="organism-title">🎯 表单组织</div>
              <div class="form-organism">
                <div class="form-field">
                  <label>用户名</label>
                  <input type="text" placeholder="请输入用户名" />
                </div>
                <div class="form-field">
                  <label>密码</label>
                  <input type="password" placeholder="请输入密码" />
                </div>
                <button class="submit-btn">提交</button>
              </div>
              <div class="organism-composition">
                包含: 表单字段分子(Label原子+Input原子) × N
              </div>
            </div>
          </div>
        </div>

        <!-- 层级连接箭头 -->
        <div class="level-arrow">▼ Organisms 组合成 Templates ▼</div>

        <!-- Level 4: Templates 展示区 -->
        <div class="level-section">
          <div class="level-badge">📐 Level 4: Templates (模板)</div>
          <p class="level-desc">定义页面的布局结构和内容区域</p>
          <div class="templates-showcase">
            <div class="template-card">
              <div class="template-title">左右两栏布局模板</div>
              <div class="two-column-template">
                <div class="sidebar-placeholder">
                  <div class="placeholder-content">侧边栏区域<br>(导航/个人资料等组织)</div>
                </div>
                <div class="main-placeholder">
                  <div class="placeholder-content">主内容区域<br>(文章列表/表单等组织)</div>
                </div>
              </div>
              <div class="template-composition">布局结构: 侧边栏组织 + 主内容组织</div>
            </div>
            <div class="template-card">
              <div class="template-title">卡片式网格模板</div>
              <div class="grid-template">
                <div class="grid-item">卡片1</div>
                <div class="grid-item">卡片2</div>
                <div class="grid-item">卡片3</div>
                <div class="grid-item">卡片4</div>
              </div>
              <div class="template-composition">响应式网格布局，可容纳任意数量的卡片组织</div>
            </div>
            <div class="template-card">
              <div class="template-title">博客文章模板</div>
              <div class="blog-template-demo">
                <div class="blog-header-placeholder">文章头部</div>
                <div class="blog-body-placeholder">文章内容区域</div>
                <div class="blog-footer-placeholder">评论区组织</div>
              </div>
              <div class="template-composition">头部 + 内容 + 底部评论的标准文章布局</div>
            </div>
          </div>
        </div>

        <!-- 层级连接箭头 -->
        <div class="level-arrow">▼ Templates 填充内容成为 Pages ▼</div>

        <!-- Level 5: Pages 展示区 -->
        <div class="level-section">
          <div class="level-badge">🌐 Level 5: Pages (页面)</div>
          <p class="level-desc">具体内容的实例化页面，是最终用户看到的结果</p>

          <!-- 页面预览 -->
          <div class="pages-showcase">
            <div class="page-preview" @click="currentPage = 'home'">
              <div class="preview-header">🏠 首页</div>
              <div class="preview-content">
                <div class="preview-nav">导航栏组织</div>
                <div class="preview-main">
                  <div class="preview-card">文章列表组织</div>
                  <div class="preview-card">侧边栏组织</div>
                </div>
              </div>
            </div>
            <div class="page-preview" @click="currentPage = 'detail'">
              <div class="preview-header">📄 详情页</div>
              <div class="preview-content">
                <div class="preview-nav">导航栏组织</div>
                <div class="preview-detail">
                  <div class="detail-header">文章标题组织</div>
                  <div class="detail-body">文章内容组织</div>
                  <div class="detail-footer">评论列表组织</div>
                </div>
              </div>
            </div>
            <div class="page-preview" @click="currentPage = 'user'">
              <div class="preview-header">👤 个人中心</div>
              <div class="preview-content">
                <div class="preview-nav">导航栏组织</div>
                <div class="preview-user">
                  <div class="user-sidebar">用户信息组织</div>
                  <div class="user-main">表单组织 / 数据列表组织</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 当前选中的页面完整展示 -->
          <div class="active-page-demo">
            <div class="active-page-title">当前选中页面: {{ pageNames[currentPage] }}</div>
            <div class="page-render">
              <!-- 首页完整渲染 -->
              <div v-if="currentPage === 'home'" class="full-page-demo">
                <div class="demo-navbar">✨ 导航栏组织 ✨</div>
                <div class="demo-two-col">
                  <div class="demo-sidebar">
                    <div class="demo-widget">📊 个人资料组织</div>
                    <div class="demo-widget">🏷️ 分类列表组织</div>
                  </div>
                  <div class="demo-content">
                    <div class="demo-article" v-for="i in 3" :key="i">
                      <div class="demo-article-title">📝 文章标题 {{ i }}</div>
                      <div class="demo-article-summary">这是文章的摘要内容，由多个分子组件组合而成...</div>
                    </div>
                    <div class="demo-pagination">⏮️ 1 2 3 ⏭️</div>
                  </div>
                </div>
              </div>

              <!-- 详情页完整渲染 -->
              <div v-if="currentPage === 'detail'" class="full-page-demo">
                <div class="demo-navbar">✨ 导航栏组织 ✨</div>
                <div class="demo-detail">
                  <div class="detail-title">🎯 深入理解原子设计系统</div>
                  <div class="detail-meta">作者: 张三 | 发布时间: 2024-01-15 | 阅读: 2.3k</div>
                  <div class="detail-content">
                    <p>原子设计系统是由Brad Frost提出的一种设计方法论，它将UI界面拆分为五个不同的层级：原子、分子、组织、模板和页面...</p>
                    <p>这种分层方法使得设计系统更加模块化、可维护和可扩展...</p>
                  </div>
                  <div class="detail-comments">
                    <div class="comment-title">💬 评论列表组织 (3条评论)</div>
                    <div class="comment-item">用户A: 非常好的文章！</div>
                    <div class="comment-item">用户B: 学习了，感谢分享</div>
                  </div>
                </div>
              </div>

              <!-- 个人中心完整渲染 -->
              <div v-if="currentPage === 'user'" class="full-page-demo">
                <div class="demo-navbar">✨ 导航栏组织 ✨</div>
                <div class="demo-profile">
                  <div class="profile-sidebar">
                    <div class="profile-avatar">👤</div>
                    <div class="profile-name">张三</div>
                    <div class="profile-stats">文章: 23 | 粉丝: 128</div>
                  </div>
                  <div class="profile-main">
                    <div class="form-group">
                      <label>昵称</label>
                      <input type="text" value="张三" />
                    </div>
                    <div class="form-group">
                      <label>邮箱</label>
                      <input type="email" value="zhangsan@example.com" />
                    </div>
                    <button class="save-btn">保存修改</button>
                  </div>
                </div>
              </div>
            </div>
            <div class="page-composition">
              页面 = 模板(Template) + 具体数据(Content) = 最终用户看到的完整界面
            </div>
          </div>
        </div>

        <!-- 层级总结 -->
        <div class="level-summary">
          <div class="summary-title">🎯 原子设计系统层级总结</div>
          <div class="summary-steps">
            <div class="step">Atoms<br>原子</div>
            <div class="step-arrow">→</div>
            <div class="step">Molecules<br>分子</div>
            <div class="step-arrow">→</div>
            <div class="step">Organisms<br>组织</div>
            <div class="step-arrow">→</div>
            <div class="step">Templates<br>模板</div>
            <div class="step-arrow">→</div>
            <div class="step">Pages<br>页面</div>
          </div>
          <div class="summary-desc">
            从最小的UI单元开始，逐步组合成更复杂的组件，最终形成完整的页面。<br>
            这种分层方法提高了代码复用性、维护性和团队协作效率。
          </div>
        </div>
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
/* ==================== 设计令牌 (Design Tokens) ==================== */
$primary-color: #3b82f6;
$success-color: #10b981;
$warning-color: #f59e0b;
$error-color: #ef4444;
$text-primary: #1f2937;
$text-secondary: #6b7280;
$border-color: #e5e7eb;
$bg-light: #f9fafb;
$bg-white: #ffffff;
$shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
$border-radius: 8px;

/* ==================== Atoms (原子层) ==================== */
// 颜色原子
.color-box {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  margin: 4px;

  &.primary { background: $primary-color; }
  &.success { background: $success-color; }
  &.warning { background: $warning-color; }
  &.error { background: $error-color; }
}

// 文字原子
.text-h1 {
  font-size: 28px;
  font-weight: bold;
  margin: 4px 0;
}
.text-h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 4px 0;
}
.text-body {
  font-size: 16px;
  margin: 4px 0;
}
.text-caption {
  font-size: 12px;
  color: $text-secondary;
  margin: 4px 0;
}

// 按钮原子
.btn-primary {
  background: $primary-color;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover { background: darken($primary-color, 10%); }
}

.btn-default {
  background: $bg-white;
  color: $text-primary;
  border: 1px solid $border-color;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;

  &:hover { background: $bg-light; }
}

.btn-text {
  background: transparent;
  color: $primary-color;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;

  &:hover { background: rgba($primary-color, 0.1); }
}

// 输入框原子
.input-base {
  padding: 8px 12px;
  border: 1px solid $border-color;
  border-radius: 6px;
  font-size: 14px;
  margin: 4px;

  &:focus {
    outline: none;
    border-color: $primary-color;
    box-shadow: 0 0 0 3px rgba($primary-color, 0.1);
  }

  &:disabled {
    background: $bg-light;
    cursor: not-allowed;
  }
}

// 间距原子展示
.spacing-item {
  background: $primary-color;
  color: white;
  text-align: center;
  border-radius: 4px;
  margin: 4px;

  &.xs { padding: 4px; font-size: 12px; }
  &.sm { padding: 8px; font-size: 12px; }
  &.md { padding: 16px; font-size: 12px; }
  &.lg { padding: 24px; font-size: 12px; }
}

/* ==================== Molecules (分子层) ==================== */
// 搜索分子
.search-molecule {
  display: flex;
  gap: 8px;
  margin: 12px 0;

  .search-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid $border-color;
    border-radius: 6px;
    font-size: 14px;
  }

  .search-btn {
    background: $primary-color;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    cursor: pointer;
  }
}

// 用户卡片分子
.user-card-molecule {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: $bg-light;
  border-radius: 8px;
  margin: 12px 0;

  .user-avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, $primary-color, darken($primary-color, 20%));
    border-radius: 50%;
  }

  .user-info {
    flex: 1;

    .user-name {
      font-weight: 600;
      margin-bottom: 4px;
    }

    .user-role {
      font-size: 12px;
      color: $text-secondary;
    }
  }

  .follow-btn {
    background: $primary-color;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
  }
}

// 评分分子
.rating-molecule {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;

  .star {
    color: #fbbf24;
    font-size: 20px;
    cursor: pointer;

    &:hover { transform: scale(1.1); }
  }

  .rating-text {
    font-size: 14px;
    color: $text-secondary;
  }
}

/* ==================== Organisms (组织层) ==================== */
// 导航栏组织
.navbar-organism {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: $bg-white;
  border-bottom: 1px solid $border-color;

  .logo {
    font-size: 18px;
    font-weight: bold;
    color: $primary-color;
  }

  .nav-links {
    display: flex;
    gap: 20px;

    .nav-link {
      text-decoration: none;
      color: $text-primary;

      &:hover { color: $primary-color; }
    }
  }

  .search-molecule-mini {
    input {
      padding: 6px 12px;
      border: 1px solid $border-color;
      border-radius: 6px;
    }
  }
}

// 文章列表组织
.article-list-organism {
  .article-item {
    padding: 12px;
    border-bottom: 1px solid $border-color;

    .article-title {
      font-weight: 600;
      margin-bottom: 4px;
    }

    .article-meta {
      font-size: 12px;
      color: $text-secondary;
      margin-bottom: 4px;
    }

    .article-summary {
      font-size: 14px;
      color: $text-secondary;
    }
  }
}

// 表单组织
.form-organism {
  .form-field {
    margin-bottom: 16px;

    label {
      display: block;
      margin-bottom: 6px;
      font-size: 14px;
      font-weight: 500;
    }

    input {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid $border-color;
      border-radius: 6px;
    }
  }

  .submit-btn {
    width: 100%;
    background: $primary-color;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 6px;
    cursor: pointer;

    &:hover { background: darken($primary-color, 10%); }
  }
}

/* ==================== Templates (模板层) ==================== */
.two-column-template {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  min-height: 200px;

  .sidebar-placeholder, .main-placeholder {
    background: $bg-light;
    border-radius: 8px;
    padding: 20px;
    text-align: center;

    .placeholder-content {
      color: $text-secondary;
    }
  }
}

.grid-template {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;

  .grid-item {
    background: $bg-light;
    padding: 20px;
    text-align: center;
    border-radius: 8px;
    color: $text-secondary;
  }
}

.blog-template-demo {
  .blog-header-placeholder, .blog-body-placeholder, .blog-footer-placeholder {
    background: $bg-light;
    padding: 16px;
    margin-bottom: 8px;
    border-radius: 8px;
    text-align: center;
    color: $text-secondary;
  }
}

/* ==================== Pages (页面层) & 全局样式 ==================== */
.demo-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.demo-template {
  max-width: 1400px;
  margin: 0 auto;
  background: $bg-white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: $shadow-lg;
}

.page-header {
  background: linear-gradient(135deg, $primary-color, darken($primary-color, 20%));
  color: white;
  padding: 40px;
  text-align: center;

  .page-title {
    font-size: 32px;
    margin-bottom: 12px;
  }

  .page-subtitle {
    font-size: 16px;
    opacity: 0.9;
  }
}

.hierarchy-organism {
  padding: 30px;
}

.level-section {
  margin-bottom: 40px;
  animation: fadeInUp 0.6s ease-out;
}

.level-badge {
  display: inline-block;
  background: $primary-color;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.level-desc {
  color: $text-secondary;
  margin-bottom: 20px;
  font-size: 14px;
}

.level-arrow {
  text-align: center;
  color: $text-secondary;
  margin: 20px 0;
  font-size: 14px;
  font-weight: 600;
}

.atoms-showcase, .molecules-showcase, .organisms-showcase, .templates-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.atom-card, .molecule-card, .organism-card, .template-card {
  background: $bg-white;
  border: 1px solid $border-color;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-md;
  }
}

.atom-label, .molecule-title, .organism-title, .template-title {
  font-weight: 600;
  margin-bottom: 16px;
  color: $text-primary;
  font-size: 16px;
}

.color-demo, .text-demo, .button-demo, .input-demo {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.molecule-composition, .organism-composition, .template-composition {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid $border-color;
  font-size: 12px;
  color: $text-secondary;
}

.badge-atom {
  display: inline-block;
  background: $bg-light;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

// Pages 预览样式
.pages-showcase {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  .page-preview {
    background: $bg-light;
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
    border: 2px solid transparent;

    &:hover {
      transform: translateY(-4px);
      box-shadow: $shadow-md;
      border-color: $primary-color;
    }

    .preview-header {
      background: $text-primary;
      color: white;
      padding: 12px;
      text-align: center;
      font-weight: 600;
    }

    .preview-content {
      padding: 16px;

      .preview-nav {
        background: $border-color;
        padding: 8px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 12px;
        text-align: center;
      }

      .preview-main, .preview-detail, .preview-user {
        display: flex;
        gap: 8px;

        .preview-card, .detail-header, .user-sidebar {
          flex: 1;
          background: $border-color;
          padding: 8px;
          border-radius: 4px;
          font-size: 10px;
          text-align: center;
        }
      }
    }
  }
}

.active-page-demo {
  background: $bg-light;
  border-radius: 12px;
  overflow: hidden;

  .active-page-title {
    background: $text-primary;
    color: white;
    padding: 12px 20px;
    font-weight: 600;
  }

  .page-render {
    padding: 20px;
  }

  .full-page-demo {
    background: $bg-white;
    border-radius: 8px;
    overflow: hidden;

    .demo-navbar {
      background: $primary-color;
      color: white;
      padding: 12px 20px;
      font-weight: 600;
    }

    .demo-two-col, .demo-profile {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 20px;
      padding: 20px;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }

    .demo-sidebar {
      .demo-widget {
        background: $bg-light;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 8px;
      }
    }

    .demo-content {
      .demo-article {
        background: $bg-light;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 8px;

        .demo-article-title {
          font-weight: 600;
          margin-bottom: 8px;
        }

        .demo-article-summary {
          font-size: 14px;
          color: $text-secondary;
        }
      }

      .demo-pagination {
        text-align: center;
        padding: 12px;
        color: $text-secondary;
      }
    }

    .demo-detail {
      padding: 20px;

      .detail-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 12px;
      }

      .detail-meta {
        font-size: 12px;
        color: $text-secondary;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid $border-color;
      }

      .detail-content {
        line-height: 1.8;
        margin-bottom: 30px;
      }

      .detail-comments {
        .comment-title {
          font-weight: 600;
          margin-bottom: 12px;
        }

        .comment-item {
          background: $bg-light;
          padding: 10px;
          margin-bottom: 8px;
          border-radius: 6px;
        }
      }
    }

    .demo-profile {
      .profile-sidebar {
        text-align: center;
        padding: 20px;
        background: $bg-light;
        border-radius: 8px;

        .profile-avatar {
          font-size: 60px;
          margin-bottom: 12px;
        }

        .profile-name {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .profile-stats {
          font-size: 12px;
          color: $text-secondary;
        }
      }

      .profile-main {
        padding: 20px;
        background: $bg-light;
        border-radius: 8px;

        .form-group {
          margin-bottom: 16px;

          label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
          }

          input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid $border-color;
            border-radius: 6px;
          }
        }

        .save-btn {
          background: $primary-color;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;

          &:hover { background: darken($primary-color, 10%); }
        }
      }
    }
  }

  .page-composition {
    padding: 16px 20px;
    background: $primary-color;
    color: white;
    text-align: center;
    font-size: 14px;
  }
}

.level-summary {
  margin-top: 40px;
  padding: 30px;
  background: linear-gradient(135deg, $bg-light, $bg-white);
  border-radius: 12px;
  text-align: center;

  .summary-title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
    color: $text-primary;
  }

  .summary-steps {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 20px;

    .step {
      background: $primary-color;
      color: white;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      text-align: center;
      min-width: 80px;
    }

    .step-arrow {
      font-size: 20px;
      color: $primary-color;
      font-weight: bold;
    }
  }

  .summary-desc {
    color: $text-secondary;
    line-height: 1.6;
    font-size: 14px;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
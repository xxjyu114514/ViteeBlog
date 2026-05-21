// AtomicDesignSystem.vue - 主组件
<template>
  <div class="demo-container">
    <!-- 工业导航栏 - 带1px白线分割和动效指示器 -->
    <nav class="industrial-nav">
      <div class="logo-section">
        <span class="logo-icon">⚙️</span>
        <span class="logo-text">ATOMIC·ZERO</span>
        <span class="logo-badge">R0</span>
      </div>

      <div class="nav-menu">
        <div
          v-for="(item, idx) in navItems"
          :key="idx"
          class="nav-item"
          :class="{ active: activeNav === idx }"
          @click="activeNav = idx"
        >
          {{ item }}
        </div>
        <div class="nav-indicator" :style="{ transform: `translateX(${activeNav * 100}%)` }"></div>
      </div>

      <div class="nav-actions">
        <button class="btn-ghost">登录</button>
        <button class="btn-primary-sm">注册</button>
      </div>
    </nav>

    <!-- 英雄区 - 视觉重心引导 -->
    <section class="hero-section">
      <div class="hero-bg-line"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-line"></span>
          INDUSTRIAL CONFIDENCE
        </div>
        <h1 class="hero-title">
          原子设计系统<br />
          <span class="hero-accent">0圆角 · 工业自信风</span>
        </h1>
        <p class="hero-desc">
          从原子到页面，建立秩序分明的视觉层级。<br />
          每个组件都经过精密切割，硬边偏移阴影，1px白线分割。
        </p>
        <div class="hero-actions">
          <button class="btn-primary">开始使用 →</button>
          <button class="btn-outline">查看文档</button>
        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-block">
          <div class="stat-number">42+</div>
          <div class="stat-label">原子组件</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <div class="stat-number">8</div>
          <div class="stat-label">色彩系统</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-block">
          <div class="stat-number">0</div>
          <div class="stat-label">圆角半径</div>
        </div>
      </div>
    </section>

    <!-- 原子层演示 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">⚛️ 原子层</h2>
        <div class="section-line"></div>
        <span class="section-sub">最小的可复用单元</span>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>颜色原子 · 8色系统</h3>
        </div>
        <div class="color-grid">
          <div class="color-swatch" v-for="color in colorSystem" :key="color.name">
            <div class="color-box" :class="color.class"></div>
            <div class="color-label">{{ color.code }}</div>
            <div class="color-name">{{ color.name }}</div>
          </div>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>文字原子 · 层级体系</h3>
        </div>
        <div class="card-ghost">
          <div class="type-demo">
            <div class="type-item"><span class="type-tag">H1</span><span class="text-h1">标题一 · 32px 自信登场</span></div>
            <div class="type-item"><span class="type-tag">H2</span><span class="text-h2">标题二 · 24px 章节划分</span></div>
            <div class="type-item"><span class="type-tag">H3</span><span class="text-h3">标题三 · 20px 卡片标题</span></div>
            <div class="type-item"><span class="type-tag">Body</span><span class="text-body">正文文字 · 16px 主要内容展示，视线自然流转至下一区域。</span></div>
            <div class="type-item"><span class="type-tag">Caption</span><span class="text-caption">辅助文字 · 13px 说明性内容，视线引导至操作区</span></div>
          </div>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>按钮原子 · 机械反馈</h3>
        </div>
        <div class="button-demo">
          <button class="btn-primary">主要按钮</button>
          <button class="btn-secondary">次要按钮</button>
          <button class="btn-success">成功</button>
          <button class="btn-warning">警告</button>
          <button class="btn-error">危险</button>
          <button class="btn-outline">边框按钮</button>
          <button class="btn-ghost">文字按钮</button>
        </div>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>输入框 · 硬焦点边框</h3>
        </div>
        <div class="input-demo">
          <input class="input-industrial" type="text" placeholder="默认输入框" />
          <input class="input-industrial" type="text" placeholder="禁用状态" disabled />
          <div class="input-tip">获得焦点时边框变为2px，并产生硬阴影偏移</div>
        </div>
      </div>
    </div>

    <!-- 分子层 - 展示组合逻辑 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">🧩 分子层</h2>
        <div class="section-line"></div>
        <span class="section-sub">原子组合 · 功能单元</span>
      </div>

      <div class="two-col-layout">
        <div class="demo-card">
          <div class="subsection-header-sm">
            <div class="indicator-line-sm"></div>
            <h4>搜索框分子</h4>
          </div>
          <div class="search-box-industrial">
            <input type="text" placeholder="搜索文档、组件..." />
            <button>搜索</button>
          </div>
        </div>

        <div class="demo-card">
          <div class="subsection-header-sm">
            <div class="indicator-line-sm"></div>
            <h4>用户卡片分子</h4>
          </div>
          <div class="user-card-industrial">
            <div class="avatar-industrial"></div>
            <div class="user-info">
              <div class="user-name">张嘉豪</div>
              <div class="user-role">工业自信设计师</div>
            </div>
            <button class="follow-btn">+ 关注</button>
          </div>
        </div>
      </div>

      <div class="two-col-layout">
        <div class="demo-card">
          <div class="subsection-header-sm">
            <div class="indicator-line-sm"></div>
            <h4>评分分子 · 黄色星星</h4>
          </div>
          <div class="rating-industrial">
            <div class="stars">
              <span class="star active">★</span>
              <span class="star active">★</span>
              <span class="star active">★</span>
              <span class="star active">★</span>
              <span class="star">★</span>
            </div>
            <span class="rating-text">4.0分 · 来自128条硬核评价</span>
          </div>
        </div>

        <div class="demo-card">
          <div class="subsection-header-sm">
            <div class="indicator-line-sm"></div>
            <h4>菜单项分子</h4>
          </div>
          <div class="menu-industrial">
            <div class="menu-item-industrial active">
              <span class="menu-icon">🏠</span>
              <span>仪表盘</span>
              <span class="menu-arrow">→</span>
            </div>
            <div class="menu-item-industrial">
              <span class="menu-icon">👥</span>
              <span>用户管理</span>
            </div>
            <div class="menu-item-industrial">
              <span class="menu-icon">⚙️</span>
              <span>系统设置</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 组织层 · 带1px白线分割和视觉重心 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">🏗️ 组织层</h2>
        <div class="section-line"></div>
        <span class="section-sub">复合区块 · 引导视线流转</span>
      </div>

      <!-- 文章列表 - 带白线分割和悬浮动效 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>文章列表 · 1px白线分割</h3>
          <span class="header-hint">视线自然下移 →</span>
        </div>
        <div class="article-list-industrial">
          <div class="article-item-industrial" v-for="(article, idx) in articles" :key="idx">
            <div class="article-rank">{{ String(idx + 1).padStart(2, '0') }}</div>
            <div class="article-content">
              <div class="article-title">{{ article.title }}</div>
              <div class="article-meta">
                <span>{{ article.author }}</span>
                <span class="meta-divider">|</span>
                <span>{{ article.date }}</span>
                <span class="meta-divider">|</span>
                <span>{{ article.views }} 阅读</span>
              </div>
              <div class="article-summary">{{ article.summary }}</div>
            </div>
            <div class="article-link">阅读 →</div>
          </div>
        </div>
      </div>

      <!-- 表单组 - 错误提示的方向性引导 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>表单组 · 错误引导与辅助提示</h3>
        </div>
        <div class="form-industrial">
          <div class="form-group-industrial">
            <label>用户名 <span class="required">*</span></label>
            <input type="text" placeholder="请输入用户名" />
            <div class="helper-text">← 用户名长度4-20个字符，用于登录</div>
          </div>
          <div class="form-group-industrial">
            <label>邮箱</label>
            <input type="email" placeholder="example@email.com" />
          </div>
          <div class="form-group-industrial error">
            <label>密码</label>
            <input type="password" placeholder="请输入密码" />
            <div class="error-text">⚠ 密码长度至少8位，请包含数字和字母 →</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板层 · 双栏/网格布局 + 遮罩焦点演示 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">📐 模板层</h2>
        <div class="section-line"></div>
        <span class="section-sub">页面骨架 · 布局系统</span>
      </div>

      <!-- 双栏布局模板 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>双栏布局模板 · 侧栏主导航</h3>
        </div>
        <div class="layout-two-col-industrial">
          <div class="sidebar-industrial">
            <div class="sidebar-menu-item active">📊 仪表盘</div>
            <div class="sidebar-menu-item">👥 用户管理</div>
            <div class="sidebar-menu-item">📝 内容管理</div>
            <div class="sidebar-menu-item">⚙️ 系统设置</div>
            <div class="sidebar-divider"></div>
            <div class="sidebar-menu-item">🔧 偏好设置</div>
          </div>
          <div class="main-content-industrial">
            <div class="content-card">
              <div class="text-h3">欢迎回来，设计师</div>
              <div class="text-caption">今日待办 · 视线聚焦于此</div>
            </div>
            <div class="grid-3-col">
              <div class="mini-card">待办事项<br /><span class="mini-num">12</span></div>
              <div class="mini-card">进行中<br /><span class="mini-num">5</span></div>
              <div class="mini-card">已完成<br /><span class="mini-num">28</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 网格布局 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>网格布局模板</h3>
        </div>
        <div class="grid-3-col-industrial">
          <div class="grid-card"><div class="grid-icon">📁</div><div class="grid-title">项目 Alpha</div><div class="grid-desc">工业自信风设计系统</div><div class="grid-link">查看详情 →</div></div>
          <div class="grid-card"><div class="grid-icon">🎨</div><div class="grid-title">组件库 v2.0</div><div class="grid-desc">42+ 原子组件，0圆角</div><div class="grid-link">查看详情 →</div></div>
          <div class="grid-card"><div class="grid-icon">📊</div><div class="grid-title">仪表盘模板</div><div class="grid-desc">数据可视化，硬边风格</div><div class="grid-link">查看详情 →</div></div>
        </div>
      </div>
    </div>

    <!-- 页面层 · 完整页面示例 + 遮罩焦点 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">📄 页面层</h2>
        <div class="section-line"></div>
        <span class="section-sub">完整场景 · 重心演示</span>
      </div>

      <!-- 仪表盘页面 - 带焦点遮罩演示按钮 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>仪表盘页面 · 数据重心</h3>
          <button class="demo-focus-btn" @click="showFocusDemo = !showFocusDemo">演示焦点遮罩</button>
        </div>
        <div class="dashboard-industrial" :class="{ 'has-overlay': showFocusDemo }">
          <div v-if="showFocusDemo" class="focus-overlay-demo" @click="showFocusDemo = false">
            <div class="focus-content" @click.stop>
              <div class="focus-close">✕</div>
              <div class="focus-title">焦点锁定区域</div>
              <div class="focus-desc">周围区域被遮罩覆盖，视线自然聚焦于此。<br />点击遮罩关闭演示。</div>
              <button class="btn-primary-sm" @click="showFocusDemo = false">了解</button>
            </div>
          </div>
          <div class="stats-grid-industrial">
            <div class="stat-card-industrial"><div class="stat-value">1,284</div><div class="stat-label">总用户数</div><div class="stat-trend">↑ 12%</div></div>
            <div class="stat-card-industrial"><div class="stat-value">¥ 89.2k</div><div class="stat-label">总收入</div><div class="stat-trend">↑ 8%</div></div>
            <div class="stat-card-industrial"><div class="stat-value">98%</div><div class="stat-label">满意度</div><div class="stat-trend">→ 持平</div></div>
            <div class="stat-card-industrial"><div class="stat-value">24</div><div class="stat-label">进行中</div><div class="stat-trend">↓ 3</div></div>
          </div>
          <div class="activity-industrial">
            <div class="activity-header">
              <span>最近活动流 →</span>
              <button class="btn-ghost-sm">查看全部</button>
            </div>
            <div class="activity-list">
              <div class="activity-item"><span class="activity-dot"></span><span>用户评论了你的文章</span><span class="activity-time">5分钟前</span></div>
              <div class="activity-item"><span class="activity-dot"></span><span>新用户注册</span><span class="activity-time">1小时前</span></div>
              <div class="activity-item"><span class="activity-dot"></span><span>系统更新完成</span><span class="activity-time">3小时前</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置页面 - 带白线分割的设置项 -->
      <div class="subsection">
        <div class="subsection-header">
          <div class="indicator-line"></div>
          <h3>设置页面 · 方向性指示</h3>
        </div>
        <div class="settings-industrial">
          <div class="settings-group">
            <div class="settings-title">通知设置</div>
            <div class="setting-row">
              <span>邮件通知</span>
              <div class="setting-control"><span class="toggle-on">✓ 已开启</span><span class="setting-hint">→ 推荐开启</span></div>
            </div>
            <div class="setting-row">
              <span>推送通知</span>
              <div class="setting-control"><span class="toggle-off">✗ 关闭</span><span class="setting-hint">→ 点击开启</span></div>
            </div>
          </div>
          <div class="settings-group">
            <div class="settings-title">隐私设置</div>
            <div class="setting-row">
              <span>公开资料</span>
              <div class="setting-control"><span class="toggle-on">✓ 公开</span></div>
            </div>
            <div class="setting-row">
              <span>显示在线状态</span>
              <div class="setting-control"><span class="toggle-off">✗ 隐藏</span></div>
            </div>
          </div>
          <button class="btn-error-block">注销账号 →</button>
        </div>
      </div>
    </div>

    <!-- 系统总结 -->
    <div class="system-footer">
      <div class="footer-line"></div>
      <div class="footer-content">
        <div class="footer-logo">⚛️ ATOMIC·ZERO</div>
        <div class="footer-desc">原子设计系统 · 工业0圆角版<br />1px白线分割 · 硬偏移阴影 · 视觉重心引导</div>
        <div class="footer-buttons">
          <button class="btn-outline-sm">开始使用</button>
          <button class="btn-ghost-sm">查看文档</button>
        </div>
      </div>
      <div class="footer-copyright">
        <span>© 2025 工业自信设计系统</span>
        <span class="footer-metrics">42组件 · 8色 · 0圆角</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AtomicDesignZeroRadius',
  data() {
    return {
      activeNav: 0,
      showFocusDemo: false,
      navItems: ['首页', '组件', '文档', '关于'],
      colorSystem: [
        { name: '主色', class: 'primary', code: '#53b0ff' },
        { name: '深蓝', class: 'primary-deep', code: '#000eff' },
        { name: '辅色', class: 'secondary', code: '#7200ff' },
        { name: '强调', class: 'accent', code: '#f86eff' },
        { name: '警告', class: 'warning', code: '#ffec7b' },
        { name: '成功', class: 'success', code: '#51ffd6' },
        { name: '错误', class: 'error', code: '#ff0072' }
      ],
      articles: [
        {
          title: '原子设计系统实战指南',
          author: '李明',
          date: '2024-01-15',
          views: '2.3k',
          summary: '原子设计是一种构建UI系统的方法论，从最小的原子组件开始，逐步组合成分子、组织、模板和页面...'
        },
        {
          title: '暗色模式设计最佳实践',
          author: '王芳',
          date: '2024-01-10',
          views: '1.8k',
          summary: '暗色模式不仅仅是把背景变成黑色，还需要考虑对比度、色彩层次和用户舒适度...'
        },
        {
          title: '设计系统的可维护性思考',
          author: '赵雷',
          date: '2024-01-05',
          views: '1.2k',
          summary: '一个好的设计系统应该在保证一致性的同时，也具备足够的灵活性和扩展性...'
        }
      ]
    };
  }
};
</script>

<style lang="scss" scoped>
// 导入设计令牌
@import './test_scss.scss';
</style>
<template>
  <div class="test-page">
    <!-- 页面标题 -->
    <header class="page-header">
      <h1 class="page-title">CSS 样式测试页面</h1>
      <p class="page-subtitle">用于开发和测试新的 UI 组件样式</p>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      
      <!-- 按钮组件区域 -->
      <section class="component-section">
        <h2 class="section-title">按钮 (Buttons)</h2>
        <div class="button-group">
          <button class="btn btn-primary">主要按钮</button>
          <button class="btn btn-secondary">次要按钮</button>
          <button class="btn btn-accent">强调按钮</button>
          <button class="btn btn-success">成功按钮</button>
          <button class="btn btn-warning">警告按钮</button>
          <button class="btn btn-error">错误按钮</button>
          <button class="btn btn-outline">边框按钮</button>
          <button class="btn btn-text">文本按钮</button>
          <button class="btn btn-disabled" disabled>禁用按钮</button>
          <!-- 新增的大渐变按钮 -->
          <button class="btn btn-gradient-large">
            <span class="btn-icon">⚡</span>
            <span class="btn-text-right">渐变大按钮</span>
          </button>
        </div>
      </section>

      <!-- 卡片组件区域 -->
      <section class="component-section">
        <h2 class="section-title">卡片 (Cards)</h2>
        <div class="card-container">
          <!-- 基础卡片 -->
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">基础卡片</h3>
            </div>
            <div class="card-body">
              <p class="card-text">这是卡片的主要内容区域，用于展示信息。</p>
            </div>
            <div class="card-footer">
              <button class="btn btn-sm">操作按钮</button>
            </div>
          </div>

          <!-- 图文卡片 -->
          <div class="card card-featured">
            <div class="card-image">
              <img src="https://via.placeholder.com/300x200" alt="示例图片" class="card-img">
            </div>
            <div class="card-content">
              <div class="card-meta">
                <span class="card-tag">标签</span>
                <time class="card-time">2024-01-01</time>
              </div>
              <h3 class="card-title">图文卡片标题</h3>
              <p class="card-description">这是图文卡片的描述内容，通常会更详细一些。</p>
              <div class="card-actions">
                <button class="btn btn-sm btn-outline">查看详情</button>
              </div>
            </div>
          </div>

          <!-- 用户卡片 -->
          <div class="card card-user">
            <div class="user-avatar">
              <img src="https://via.placeholder.com/60x60" alt="用户头像" class="avatar-img">
            </div>
            <div class="user-info">
              <h4 class="user-name">用户名</h4>
              <p class="user-role">角色信息</p>
              <div class="user-stats">
                <span class="stat-item">文章: <strong>25</strong></span>
                <span class="stat-item">粉丝: <strong>150</strong></span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 表单组件区域 -->
      <section class="component-section">
        <h2 class="section-title">表单 (Forms)</h2>
        <form class="form">
          <div class="form-group">
            <label class="form-label" for="username">用户名</label>
            <input type="text" id="username" class="form-input" placeholder="请输入用户名">
          </div>
          
          <div class="form-group">
            <label class="form-label" for="email">邮箱</label>
            <input type="email" id="email" class="form-input" placeholder="请输入邮箱地址">
          </div>
          
          <div class="form-group">
            <label class="form-label" for="message">消息</label>
            <textarea id="message" class="form-textarea" placeholder="请输入您的消息"></textarea>
          </div>
          
          <div class="form-checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" class="checkbox-input">
              <span class="checkbox-text">同意服务条款</span>
            </label>
          </div>
          
          <div class="form-radio-group">
            <label class="radio-label">
              <input type="radio" name="gender" class="radio-input" value="male">
              <span class="radio-text">男</span>
            </label>
            <label class="radio-label">
              <input type="radio" name="gender" class="radio-input" value="female">
              <span class="radio-text">女</span>
            </label>
          </div>
        </form>
      </section>

      <!-- 文字样式区域 -->
      <section class="component-section">
        <h2 class="section-title">文字样式 (Typography)</h2>
        <div class="typography-demo">
          <h1 class="text-h1">一级标题 H1</h1>
          <h2 class="text-h2">二级标题 H2</h2>
          <h3 class="text-h3">三级标题 H3</h3>
          <h4 class="text-h4">四级标题 H4</h4>
          <h5 class="text-h5">五级标题 H5</h5>
          <h6 class="text-h6">六级标题 H6</h6>
          
          <p class="text-paragraph">这是段落文本。段落文本应该有良好的可读性，行高适中，字间距合理。</p>
          
          <p class="text-secondary">这是次要文本，通常用于描述性内容或辅助信息。</p>
          
          <p class="text-tertiary">这是三级文本，通常用于更不重要的信息。</p>
          
          <p class="text-disabled">这是禁用状态的文本。</p>
          
          <div class="text-links">
            <a href="#" class="text-link">这是一个链接</a>
            <a href="#" class="text-link link-hover">悬停链接</a>
            <a href="#" class="text-link link-active">激活链接</a>
          </div>
          
          <div class="text-emphasis">
            <strong class="text-bold">粗体文本</strong>
            <em class="text-italic">斜体文本</em>
            <code class="text-code">代码文本</code>
            <mark class="text-highlight">高亮文本</mark>
          </div>
        </div>
      </section>

      <!-- 列表组件区域 -->
      <section class="component-section">
        <h2 class="section-title">列表 (Lists)</h2>
        <div class="lists-demo">
          <ul class="list-unstyled">
            <li class="list-item">无样式列表项 1</li>
            <li class="list-item">无样式列表项 2</li>
            <li class="list-item">无样式列表项 3</li>
          </ul>
          
          <ol class="list-numbered">
            <li class="list-item">有序列表项 1</li>
            <li class="list-item">有序列表项 2</li>
            <li class="list-item">有序列表项 3</li>
          </ol>
          
          <ul class="list-bulleted">
            <li class="list-item">项目符号列表项 1</li>
            <li class="list-item">项目符号列表项 2</li>
            <li class="list-item">项目符号列表项 3</li>
          </ul>
        </div>
      </section>

      <!-- 状态指示器区域 -->
      <section class="component-section">
        <h2 class="section-title">状态和指示器 (Status & Indicators)</h2>
        <div class="status-demo">
          <div class="badge badge-primary">主要</div>
          <div class="badge badge-secondary">次要</div>
          <div class="badge badge-success">成功</div>
          <div class="badge badge-warning">警告</div>
          <div class="badge badge-error">错误</div>
          
          <div class="loading-spinner"></div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: 65%"></div>
          </div>
        </div>
      </section>

      <!-- 文章卡片区域 -->
      <section class="component-section">
        <h2 class="section-title">文章卡片 (Article Cards)</h2>
        <div class="articles-grid-single">
          <!-- 单个文章卡片 - 长度增加3倍 -->
          <div class="article-card article-card-extended">
            <div class="article-card__header">
              <h3 class="article-card__title">
                <a href="#">如何构建现代化的博客系统</a>
              </h3>
            </div>
            <div class="article-card__meta">
              <div class="article-card__author">
                <img src="https://via.placeholder.com/24x24" alt="作者头像" class="article-card__avatar">
                <span>张三</span>
              </div>
              <time>2024-01-15</time>
              <span>5 分钟阅读</span>
            </div>
            <div class="article-card__content">
              <p class="article-card__excerpt">
                这是一篇关于如何构建现代化博客系统的详细教程，涵盖了前端架构、后端设计、数据库优化等多个方面。本文将深入探讨从零开始搭建一个完整的博客平台所需要的技术栈选择、架构设计、性能优化策略以及安全防护措施。
              </p>
            </div>
            <div class="article-card__footer">
              <div class="article-card__stats">
                <span>👍 24</span>
                <span>💬 8</span>
                <span>👁️ 156</span>
              </div>
              <a href="#" class="article-card__tag article-card__tag-half-width">技术教程</a>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style lang="scss" scoped>
// 引入设计令牌
@import './test_scss.scss';
</style>
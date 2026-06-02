<template>
  <div class="test-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <h1 class="page-title">ViteeBlog 设计系统</h1>
      <p class="page-subtitle">冷色调机能风 · 明日方舟风格 · 0 圆角 · 毛玻璃系统</p>
    </header>

    <div class="main-content">
      <!-- ==================== 1. 颜色令牌展示 ==================== -->
      <section class="component-section">
        <h2 class="section-title">颜色令牌</h2>
        <div class="color-grid">
          <div class="color-item" v-for="color in colorTokens" :key="color.name">
            <div class="color-swatch" :style="{ background: color.value }"></div>
            <span class="color-name">{{ color.name }}</span>
            <span class="color-value">{{ color.value }}</span>
          </div>
        </div>
      </section>

      <!-- ==================== 2. 按钮系统 ==================== -->
      <section class="component-section">
        <h2 class="section-title">按钮系统</h2>
        <div class="button-group">
          <button class="btn btn-primary">主要按钮</button>
          <button class="btn btn-secondary">次要按钮</button>
          <button class="btn btn-accent">强调按钮</button>
          <button class="btn btn-success">成功按钮</button>
          <button class="btn btn-warning">警告按钮</button>
          <button class="btn btn-error">错误按钮</button>
        </div>
        <div class="button-group">
          <button class="btn btn-outline">边框按钮</button>
          <button class="btn btn-ghost">幽灵按钮</button>
          <button class="btn btn-glass">毛玻璃按钮</button>
          <button class="btn btn-gradient">渐变按钮</button>
        </div>
        <div class="button-group">
          <button class="btn btn-primary btn-sm">小尺寸</button>
          <button class="btn btn-primary">默认尺寸</button>
          <button class="btn btn-primary btn-lg">大尺寸</button>
          <button class="btn btn-primary" disabled>禁用状态</button>
        </div>
      </section>

      <!-- ==================== 3. 卡片系统 ==================== -->
      <section class="component-section">
        <h2 class="section-title">卡片系统</h2>

        <h3 class="subsection-title">基础卡片</h3>
        <div class="card-container">
          <div class="card" v-for="i in 3" :key="i">
            <div class="card-header">
              <h3 class="card-title">卡片标题 {{ i }}</h3>
            </div>
            <div class="card-body">
              <p class="card-text">这是一段卡片内容，展示了基础卡片的样式。冷灰色背景配合白色边框，简洁有力。</p>
            </div>
            <div class="card-footer">
              <button class="btn btn-outline btn-sm">操作按钮</button>
            </div>
          </div>
        </div>

        <h3 class="subsection-title">图文卡片</h3>
        <div class="card-container">
          <div class="card card-featured" v-for="i in 2" :key="i">
            <div class="card-image">
              <img class="card-img" :src="`https://picsum.photos/id/${10 + i}/400/200`" alt="示例图片">
            </div>
            <div class="card-content">
              <div class="card-meta">
                <span class="card-tag">文章</span>
                <span>2024-01-0{{ i }}</span>
              </div>
              <h3 class="card-title">图文卡片标题</h3>
              <p class="card-description">图文卡片适用于展示博客文章、项目作品等内容，配合图片增强视觉效果。</p>
              <div class="card-actions">
                <button class="btn btn-primary btn-sm">阅读更多</button>
              </div>
            </div>
          </div>
        </div>

        <h3 class="subsection-title">用户卡片</h3>
        <div class="card-container">
          <div class="card card-user">
            <div class="user-avatar">
              <img class="avatar-img" src="https://api.dicebear.com/7.x/avataaars/svg?seed=user1" alt="头像">
            </div>
            <div class="user-info">
              <h4 class="user-name">晓明同学</h4>
              <p class="user-role">全栈开发者</p>
              <div class="user-stats">
                <span class="stat-item"><strong>128</strong> 文章</span>
                <span class="stat-item"><strong>2.3k</strong> 粉丝</span>
              </div>
            </div>
          </div>
          <div class="card card-user">
            <div class="user-avatar">
              <div class="avatar-img" style="background: #6c5ce7;"></div>
            </div>
            <div class="user-info">
              <h4 class="user-name">方舟博士</h4>
              <p class="user-role">UI 设计师</p>
              <div class="user-stats">
                <span class="stat-item"><strong>89</strong> 文章</span>
                <span class="stat-item"><strong>1.2k</strong> 粉丝</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== 4. 文章卡片（沉浸式变体） ==================== -->
      <section class="component-section">
        <h2 class="section-title">文章卡片</h2>
        <div class="articles-grid">
          <div class="article-card" v-for="i in 4" :key="i">
            <div class="article-card__header">
              <h3 class="article-card__title">
                <a href="javascript:void(0)">深入理解 Vue 3 响应式原理 - 第 {{ i }} 部分</a>
              </h3>
              <div class="article-card__meta">
                <span class="article-card__author">
                  <img class="article-card__avatar" src="https://api.dicebear.com/7.x/avataaars/svg?seed=auth{{ i }}">
                  技术作者
                </span>
                <span>2024-01-0{{ i }}</span>
                <span>· 10 分钟阅读</span>
              </div>
            </div>
            <div class="article-card__content">
              <p class="article-card__excerpt">
                Vue 3 的响应式系统基于 Proxy 实现，相比 Vue 2 的 Object.defineProperty 有诸多优势...
              </p>
            </div>
            <div class="article-card__footer">
              <div class="article-card__stats">
                <span>❤️ 128</span>
                <span>💬 24</span>
              </div>
              <a href="javascript:void(0)" class="article-card__tag">#Vue.js</a>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== 5. 表单系统 ==================== -->
      <section class="component-section">
        <h2 class="section-title">表单系统</h2>
        <div class="form">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input type="text" class="form-input" placeholder="请输入用户名">
          </div>
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input type="email" class="form-input" placeholder="user@example.com">
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input type="password" class="form-input" placeholder="请输入密码">
          </div>
          <div class="form-group">
            <label class="form-label">个人简介</label>
            <textarea class="form-textarea" placeholder="介绍一下你自己..."></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">选择角色</label>
            <select class="form-select">
              <option>普通用户</option>
              <option>编辑者</option>
              <option>管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">错误状态示例</label>
            <input type="text" class="form-input is-error" value="错误的内容">
            <span class="form-error-text">请输入正确的格式</span>
          </div>
          <div class="form-group">
            <div class="form-checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" class="checkbox-input"> 同意用户协议
              </label>
              <label class="checkbox-label">
                <input type="checkbox" class="checkbox-input"> 接收邮件通知
              </label>
            </div>
          </div>
          <div class="form-group">
            <div class="form-radio-group">
              <label class="radio-label">
                <input type="radio" name="gender" class="radio-input"> 男
              </label>
              <label class="radio-label">
                <input type="radio" name="gender" class="radio-input"> 女
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">毛玻璃输入框</label>
            <input type="text" class="form-input form-input-glass" placeholder="毛玻璃效果">
          </div>
          <div class="button-group">
            <button class="btn btn-primary">提交表单</button>
            <button class="btn btn-outline">重置</button>
          </div>
        </div>
      </section>

      <!-- ==================== 6. 毛玻璃系统 ==================== -->
      <section class="component-section glass-showcase">
        <h2 class="section-title" style="color: #fff;">毛玻璃系统</h2>

        <h3 class="subsection-title" style="color: #fff;">毛玻璃面板</h3>
        <div class="glass-grid" style="margin-bottom: 24px;">
          <div class="glass-panel" style="padding: 24px;">
            <div class="glass-card__title">深色毛玻璃面板</div>
            <div class="glass-card__body">基础毛玻璃效果，适用于深色背景上的卡片容器。</div>
          </div>
          <div class="glass-panel--light" style="padding: 24px;">
            <div class="glass-card__title">浅色毛玻璃面板</div>
            <div class="glass-card__body">更透亮的毛玻璃效果，适合轻量级装饰面板。</div>
          </div>
          <div class="glass-panel--brand" style="padding: 24px;">
            <div class="glass-card__title">品牌色毛玻璃面板</div>
            <div class="glass-card__body">带冰蓝色调的毛玻璃，适合重点区域。</div>
          </div>
        </div>

        <h3 class="subsection-title" style="color: #fff;">毛玻璃卡片</h3>
        <div class="glass-card-grid">
          <div class="glass-card-item" v-for="i in 4" :key="i">
            <span class="glass-card-item__icon">⚙️</span>
            <h4 class="glass-card-item__title">功能模块 {{ i }}</h4>
            <p class="glass-card-item__desc">这是毛玻璃卡片的描述文字，展示在模拟渐变背景上的效果。</p>
          </div>
        </div>
      </section>

      <!-- ==================== 7. 标签/徽章系统 ==================== -->
      <section class="component-section">
        <h2 class="section-title">标签 & 徽章</h2>
        <div class="status-demo">
          <span class="badge badge-primary">主要</span>
          <span class="badge badge-secondary">次要</span>
          <span class="badge badge-accent">强调</span>
          <span class="badge badge-success">成功</span>
          <span class="badge badge-warning">警告</span>
          <span class="badge badge-error">错误</span>
          <span class="badge badge-glass">毛玻璃</span>
          <span class="badge badge-outline">描边</span>
        </div>
        <div class="status-demo" style="margin-top: 16px;">
          <span class="badge badge-primary">前端</span>
          <span class="badge badge-primary">Vue</span>
          <span class="badge badge-primary">React</span>
          <span class="badge badge-secondary">设计系统</span>
          <span class="badge badge-glass">暗色主题</span>
        </div>
      </section>

      <!-- ==================== 8. 文字排版 ==================== -->
      <section class="component-section">
        <h2 class="section-title">文字排版</h2>
        <div class="typography-demo">
          <h1 class="text-h1">H1 一级标题 · 等宽字体</h1>
          <h2 class="text-h2">H2 二级标题 · 工程感</h2>
          <h3 class="text-h3">H3 三级标题 · 冷色调</h3>
          <h4 class="text-h4">H4 四级标题 · 机能风</h4>
          <h5 class="text-h5">H5 五级标题 · 无衬线体</h5>
          <h6 class="text-h6">H6 六级标题 · 保持克制</h6>

          <p class="text-paragraph">
            正文段落示例。这是一个典型的博客文章段落，展示了正文的字体、行高和颜色。冷色调主题下，主文字使用亮白色，保证在暗色背景上的可读性。正文行高 1.6-1.75，提供舒适的阅读体验。
          </p>
          <p class="text-secondary">次要文字层级 · 用于描述、补充信息等</p>
          <p class="text-tertiary">辅助文字层级 · 时间戳、统计数字等</p>
          <p class="text-disabled">禁用文字 · 不可用状态的提示文字</p>

          <div class="text-links">
            <a href="javascript:void(0)" class="text-link">普通链接</a>
            <a href="javascript:void(0)" class="text-link">访问文档</a>
            <a href="javascript:void(0)" class="text-link">返回首页</a>
          </div>

          <div class="text-emphasis">
            <span class="text-bold">粗体文字</span>
            <span class="text-italic">斜体文字</span>
            <code class="text-code">console.log("内联代码")</code>
            <span class="text-highlight">高亮文字背景</span>
            <span class="text-strikethrough">删除线文字</span>
          </div>
        </div>
      </section>

      <!-- ==================== 9. 列表系统 ==================== -->
      <section class="component-section">
        <h2 class="section-title">列表系统</h2>
        <div class="lists-demo" style="display: flex; gap: 48px; flex-wrap: wrap;">
          <div>
            <h4>无序列表</h4>
            <ul class="list-bulleted">
              <li class="list-item">冷色调设计语言</li>
              <li class="list-item">0 圆角硬边风格</li>
              <li class="list-item">毛玻璃视觉效果</li>
              <li class="list-item">响应式布局支持</li>
            </ul>
          </div>
          <div>
            <h4>有序列表</h4>
            <ol class="list-numbered">
              <li class="list-item">安装依赖</li>
              <li class="list-item">配置主题</li>
              <li class="list-item">导入组件</li>
              <li class="list-item">开始使用</li>
            </ol>
          </div>
          <div>
            <h4>无样式列表</h4>
            <ul class="list-unstyled">
              <li class="list-item">✦ 自定义圆点样式</li>
              <li class="list-item">✦ 纯净列表结构</li>
              <li class="list-item">✦ 灵活扩展</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- ==================== 10. 进度条 ==================== -->
      <section class="component-section">
        <h2 class="section-title">进度条</h2>
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <div>
            <p style="margin-bottom: 8px;">加载进度 45%</p>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 45%;"></div>
            </div>
          </div>
          <div>
            <p style="margin-bottom: 8px;">加载进度 78%</p>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 78%;"></div>
            </div>
          </div>
          <div>
            <p style="margin-bottom: 8px;">加载进度 100%</p>
            <div class="progress-bar">
              <div class="progress-fill" style="width: 100%;"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== 11. 加载状态 ==================== -->
      <section class="component-section">
        <h2 class="section-title">加载状态</h2>
        <div style="display: flex; gap: 48px; align-items: center; flex-wrap: wrap;">
          <div class="loading-state" style="padding: 0;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 12px;">加载中...</p>
          </div>
          <div class="loading-spinner" style="width: 30px; height: 30px;"></div>
          <div class="loading-spinner" style="width: 40px; height: 40px; border-width: 3px;"></div>
          <div class="loading-spinner" style="width: 50px; height: 50px; border-width: 4px;"></div>
        </div>
      </section>

      <!-- ==================== 12. 错误/空状态 ==================== -->
      <section class="component-section">
        <h2 class="section-title">错误 & 空状态</h2>
        <div style="display: flex; gap: 32px; flex-wrap: wrap;">
          <div class="error-state" style="padding: 32px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <p class="error-message">❌ 数据加载失败</p>
            <p class="text-secondary">请检查网络连接后重试</p>
            <button class="btn btn-outline btn-sm" style="margin-top: 16px;">重试</button>
          </div>
          <div class="empty-state" style="padding: 32px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div class="icon" style="font-size: 3rem;">📭</div>
            <p class="message">暂无数据</p>
            <p class="text-tertiary">点击按钮添加第一条内容</p>
            <button class="btn btn-primary btn-sm" style="margin-top: 16px;">+ 新建</button>
          </div>
        </div>
      </section>

      <!-- ==================== 13. 分割线 ==================== -->
      <section class="component-section">
        <h2 class="section-title">分割线</h2>
        <div>
          <p>普通分割线（1px 细线）</p>
          <hr class="divider" style="margin: 16px 0;">
          <p>强调分割线（更明显的对比）</p>
          <hr class="divider" style="background: rgba(255,255,255,0.12); margin: 16px 0;">
        </div>
      </section>

      <!-- ==================== 14. Hero 按钮（大按钮） ==================== -->
      <section class="component-section">
        <h2 class="section-title">Hero 大按钮</h2>
        <div class="hero-button-group" style="margin-top: 16px; background: #0d1117;">
          <div class="hero-button">
            <div class="hero-button__inner">
              <span class="hero-button__icon">📝</span>
              <div class="hero-button__text">
                <span class="hero-button__label">写文章</span>
                <span class="hero-button__sub">Write</span>
              </div>
            </div>
          </div>
          <div class="hero-button">
            <div class="hero-button__inner">
              <span class="hero-button__icon">💬</span>
              <div class="hero-button__text">
                <span class="hero-button__label">留言板</span>
                <span class="hero-button__sub">Message</span>
              </div>
            </div>
          </div>
          <div class="hero-button">
            <div class="hero-button__inner">
              <span class="hero-button__icon">👤</span>
              <div class="hero-button__text">
                <span class="hero-button__label">关于我</span>
                <span class="hero-button__sub">About</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== 15. 玻璃大卡片 ==================== -->
      <section class="component-section">
        <h2 class="section-title">玻璃大卡片</h2>
        <div class="glass-hero-card-showcase" style="margin-top: 16px;">
          <div class="glass-hero-card">
            <div class="glass-hero-card__inner">
              <h3 class="glass-hero-card__title">ViteeBlog</h3>
              <p class="glass-hero-card__desc">
                冷色调机能风设计系统，融合明日方舟美学与 GitHub 暗色层次，打造独特的博客体验。
              </p>
              <div class="glass-hero-card__meta">
                <span>设计系统 v2.0</span>
                <span>0 圆角 · 硬边美学</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// 颜色令牌数据
const colorTokens = [
  { name: '主色', value: '#58a6ff' },
  { name: '辅色', value: '#6c5ce7' },
  { name: '强调色', value: '#00cec9' },
  { name: '成功', value: '#2ea043' },
  { name: '警告', value: '#d29922' },
  { name: '错误', value: '#da3633' },
  { name: '底色', value: '#0d1117' },
  { name: '面板底色', value: '#1c2128' },
  { name: '悬浮层', value: '#2d333b' },
  { name: '主文字', value: '#B0B8C5' },
  { name: '次要文字', value: '#8b949e' },
]
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/mixins' as *;

// 页面特有样式
.test-page {
  background: $bg-base;
  color: $text-primary;
  font-family: $font-sans;
  min-height: 100vh;
  padding: $space-lg;

  *,
  *::before,
  *::after {
    border-radius: 0;
  }
}

.page-header {
  text-align: center;
  margin-bottom: $space-2xl;
  padding: $space-xl 0;

  .page-title {
    font-family: $font-mono;
    font-size: 2.2rem;
    font-weight: 700;
    color: $color-primary;
    margin-bottom: $space-xs;
    letter-spacing: -0.02em;
  }

  .page-subtitle {
    font-size: 1rem;
    color: $text-secondary;
  }
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.component-section {
  margin-bottom: $space-2xl;
  padding: $space-xl;
  background: $bg-surface;
  border: $border-white-light;

  .section-title {
    font-family: $font-mono;
    font-size: 1.4rem;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: $space-lg;
    padding-bottom: $space-sm;
    border-bottom: $divider-emphasis;
    letter-spacing: 0.02em;
  }
}

.subsection-title {
  font-family: $font-mono;
  font-size: 1.1rem;
  font-weight: 600;
  color: $text-secondary;
  margin: $space-lg 0 $space-md;
  padding-left: $space-sm;
  border-left: 3px solid $color-primary;
}

// 颜色网格
.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: $space-md;
}

.color-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: $space-xs;

  .color-swatch {
    width: 80px;
    height: 80px;
    border: $border-white-light;
  }

  .color-name {
    font-size: 0.85rem;
    font-weight: 500;
    color: $text-primary;
  }

  .color-value {
    font-size: 0.7rem;
    font-family: $font-mono;
    color: $text-tertiary;
  }
}

// 按钮组容器
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: $space-md;
  margin-bottom: $space-lg;
}

// 卡片容器
.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: $space-lg;
  margin-bottom: $space-lg;
}

// 文章网格
.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $space-lg;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: $space-md;
  }
}

// 毛玻璃卡片网格
.glass-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: $space-lg;
}

// 状态演示
.status-demo {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: $space-md;
}

// 加载状态
.loading-state {
  text-align: center;
  .loading-spinner {
    width: 40px;
    height: 40px;
    margin: 0 auto;
  }
}

// 错误/空状态
.error-state, .empty-state {
  flex: 1;
  min-width: 200px;
}

.error-message {
  color: $color-error;
}

// 响应式调整
@media (max-width: 768px) {
  .test-page {
    padding: $space-md;
  }
  .component-section {
    padding: $space-md;
  }
  .glass-card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
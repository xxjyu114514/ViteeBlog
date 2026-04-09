<template>
  <div class="post-list-wrapper container-narrow">
    <div class="tab-header">
      <button 
        :class="{ active: currentTab === 'latest' }" 
        @click="currentTab = 'latest'"
      >最新文章</button>
      <button 
        :class="{ active: currentTab === 'hot' }" 
        @click="currentTab = 'hot'"
      >热门文章</button>
    </div>

    <div class="list-content">
      <PostItem 
        v-for="article in filteredArticles" 
        :key="article.id" 
        :post="article" 
        class="post-item-card"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PostItem from './PostItem.vue'

const currentTab = ref('latest')

const articles = ref([
  { id: 1, title: '如何使用 Vite 快速构建项目', summary: 'Vite 是下一代前端工具链，能够显著提升前端开发体验。', date: '2026-04-01', views: 120, type: 'latest' },
{ id: 2, title: 'Vue3 组合式 API 实战', summary: 'Setup 语法糖让你的代码更简洁，逻辑更易于复用 and 维护。', date: '2026-03-28', views: 540, type: 'hot' },
{ id: 3, title: 'CSS 现代布局指南', summary: '从 Flexbox 到 Grid，掌握现代 Web 布局的核心技术。', date: '2026-03-15', views: 320, type: 'latest' },
{ id: 4, title: 'TypeScript 泛型深入理解', summary: '泛型是 TypeScript 最强大的特性之一，掌握它能写出更灵活的代码。', date: '2026-03-10', views: 280, type: 'latest' },
{ id: 5, title: 'Pinia 状态管理最佳实践', summary: 'Pinia 是 Vue 官方推荐的状态管理库，轻量且强大。', date: '2026-03-05', views: 890, type: 'hot' },
{ id: 6, title: '前端性能优化完全指南', summary: '从加载速度到运行时性能，全方位提升应用体验。', date: '2026-02-28', views: 1500, type: 'hot' },
{ id: 7, title: 'Nuxt3 服务端渲染入门', summary: '使用 Nuxt3 轻松构建 SEO 友好的 Vue 应用。', date: '2026-02-20', views: 210, type: 'latest' },
{ id: 8, title: 'TailwindCSS 实用技巧', summary: '原子化 CSS 框架的最佳实践，让你写样式更高效。', date: '2026-02-15', views: 430, type: 'latest' },
{ id: 9, title: 'Vue Router 4 源码解析', summary: '深入理解 Vue Router 的实现原理，掌握路由核心机制。', date: '2026-02-10', views: 670, type: 'hot' },
{ id: 10, title: '前端自动化测试入门', summary: '使用 Vitest 和 Vue Test Utils 为应用保航。', date: '2026-02-01', views: 180, type: 'latest' },
{ id: 11, title: 'Webpack vs Vite 对比分析', summary: '从构建原理到开发体验，全面对比两大构建工具。', date: '2026-01-25', views: 3200, type: 'hot' },
{ id: 12, title: 'JavaScript 设计模式实战', summary: '单例、工厂、观察者...经典设计模式在前端中的应用。', date: '2026-01-20', views: 950, type: 'hot' },
{ id: 13, title: 'Node.js 后端开发入门', summary: '使用 Express + MongoDB 快速搭建 RESTful API。', date: '2026-01-15', views: 340, type: 'latest' },
{ id: 14, title: 'Three.js 3D 可视化', summary: '在浏览器中创建令人惊艳的 3D 场景和动画。', date: '2026-01-10', views: 560, type: 'latest' },
{ id: 15, title: 'Git 协作开发最佳实践', summary: '分支管理策略、Commit 规范、Code Review 流程。', date: '2026-01-05', views: 780, type: 'hot' },
{ id: 16, title: 'ES2025 新特性一览', summary: '探索 JavaScript 最新特性，保持技术前沿。', date: '2026-01-01', views: 420, type: 'latest' },
{ id: 17, title: '前端安全防护指南', summary: 'XSS、CSRF、SQL注入...常见安全问题及解决方案。', date: '2025-12-28', views: 1100, type: 'hot' },
{ id: 18, title: '微前端架构实践', summary: '使用 qiankun 实现大型应用的技术融合和独立部署。', date: '2025-12-20', views: 890, type: 'latest' },
{ id: 19, title: 'Docker 前端开发环境', summary: '容器化开发环境，解决环境不一致的问题。', date: '2025-12-15', views: 310, type: 'latest' },
{ id: 20, title: 'GraphQL 从入门到实践', summary: '相比 REST API，GraphQL 提供了更灵活的数据查询方式。', date: '2025-12-10', views: 650, type: 'hot' },
{ id: 21, title: 'Vue3 响应式原理', summary: '深入理解 Proxy 和 Reflect 如何实现响应式系统。', date: '2025-12-05', views: 2100, type: 'hot' },
{ id: 22, title: 'Chrome DevTools 调试技巧', summary: '用好开发者工具，让 bug 无处遁形。', date: '2025-11-28', views: 480, type: 'latest' },
{ id: 23, title: 'PWA 渐进式应用开发', summary: '让 Web 应用具备原生应用的离线缓存和推送能力。', date: '2025-11-20', views: 290, type: 'latest' },
{ id: 24, title: 'WebAssembly 实战', summary: '使用 Rust 编写高性能的 Web 模块。', date: '2025-11-15', views: 370, type: 'latest' },
{ id: 25, title: 'Monorepo 管理大型项目', summary: '使用 pnpm workspace 或 Turborepo 管理多包项目。', date: '2025-11-10', views: 830, type: 'hot' }
])

const filteredArticles = computed(() => {
  return currentTab.value === 'latest' 
    ? [...articles.value].sort((a, b) => b.id - a.id)
    : [...articles.value].sort((a, b) => b.views - a.views)
})
</script>

<style lang="scss" scoped>
.post-list-wrapper {
  padding: 60px 24px; // 增加顶部高度，避开固定导航栏
}

.tab-header {
  display: flex;
  gap: 40px; 
  border-bottom: 1px solid rgba(0, 0, 0, 0.06); // 极淡的底线
  margin-bottom: 40px;
  
  button {
    padding: 14px 4px;
    background: none;
    border: none;
    font-size: 1.05rem;
    color: var(--text-secondary);
    cursor: pointer;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      color: var(--text-main);
    }

    &.active {
      color: var(--primary-color);
      font-weight: 600;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 100%;
        height: 2.5px;
        background: var(--primary-color);
        border-radius: 4px 4px 0 0; // 顶部微圆角
      }
    }
  }
}

.list-content {
  display: flex;
  flex-direction: column;
  gap: 24px; // 帖子卡片之间的间距
}
</style>
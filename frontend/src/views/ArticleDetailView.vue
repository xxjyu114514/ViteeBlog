<template>
  <div class="article-detail-wrapper page-wrapper-base">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="content-container container">
      <!-- 文章加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton-title"></div>
        <div class="skeleton-meta"></div>
        <div class="skeleton-content"></div>
        <div class="skeleton-content"></div>
        <div class="skeleton-content"></div>
      </div>
      
      <!-- 文章内容 -->
      <div v-else-if="article" class="article-content">
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta meta-text">
          <span class="author">作者：{{ article.author || '观测笔记' }}</span>
          <span class="dot">·</span>
          <span class="date">{{ article.date }}</span>
          <span class="dot">·</span>
          <span class="views">{{ article.views }} 阅读</span>
        </div>
        
        <div class="article-body" v-html="article.content"></div>
        
        <!-- 文章标签 -->
        <div v-if="article.tags && article.tags.length" class="article-tags">
          <span class="tag" v-for="tag in article.tags" :key="tag">
            #{{ tag }}
          </span>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <div v-else class="error-state">
        <div class="error-icon">⚠️</div>
        <p class="error-message">{{ errorMessage || '文章加载失败，请稍后重试' }}</p>
        <button @click="loadArticle" class="retry-button">重新加载</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 路由和状态
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 文章数据和状态
const article = ref(null)
const loading = ref(true)
const errorMessage = ref('')

// 获取文章ID
const articleId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id) : null
})

// 预设的两篇详细文章
const detailedArticles = {
  1: {
    id: 1,
    title: '如何使用 Vite 快速构建项目',
    author: '观测笔记',
    date: '2026-04-01',
    views: 120,
    tags: ['Vite', '前端构建', '开发工具'],
    content: `
      <p>Vite 是下一代前端构建工具，由 Vue.js 作者尤雨溪开发，旨在提供更快的开发体验。</p>
      
      <h2>为什么选择 Vite？</h2>
      <p>Vite 利用现代浏览器的原生 ES 模块支持，在开发环境中实现了按需编译，大大提升了启动速度和热更新性能。</p>
      
      <h3>核心特性</h3>
      <ul>
        <li><strong>极速冷启动</strong>：无需等待整个应用编译完成</li>
        <li><strong>即时热更新</strong>：模块热替换速度极快</li>
        <li><strong>丰富的插件生态</strong>：兼容 Rollup 插件</li>
        <li><strong>内置优化</strong>：自动代码分割、预加载等</li>
      </ul>
      
      <h3>快速开始</h3>
      <pre><code>npm create vite@latest my-vue-app -- --template vue
cd my-vue-app
npm install
npm run dev</code></pre>
      
      <p>通过以上简单的命令，你就可以拥有一个功能完整的 Vue 3 + Vite 开发环境。</p>
      
      <h3>生产构建</h3>
      <p>Vite 使用 Rollup 进行生产构建，生成高度优化的静态资源：</p>
      <pre><code>npm run build</code></pre>
      
      <p>构建后的应用体积小、加载快，适合生产环境部署。</p>
      
      <blockquote>
        <p>Vite 的设计理念是"开发即生产"，让开发体验和生产性能都达到最佳状态。</p>
      </blockquote>
      
      <p>如果你还在使用传统的 Webpack 开发流程，强烈建议尝试 Vite，它会让你的开发效率提升数倍！</p>
    `
  },
  2: {
    id: 2,
    title: 'Vue3 组合式 API 实战',
    author: '观测笔记',
    date: '2026-03-28',
    views: 540,
    tags: ['Vue3', 'Composition API', '前端框架'],
    content: `
      <p>Vue 3 引入的组合式 API (Composition API) 彻底改变了 Vue 应用的组织方式。</p>
      
      <h2>从 Options API 到 Composition API</h2>
      <p>在 Vue 2 中，我们使用 Options API 来组织组件逻辑，但当组件变得复杂时，相关的逻辑会被分散到不同的选项中。</p>
      
      <h3>组合式 API 的优势</h3>
      <ul>
        <li><strong>更好的逻辑复用</strong>：通过自定义 Hook 函数</li>
        <li><strong>更清晰的代码组织</strong>：相关逻辑集中在一起</li>
        <li><strong>更好的 TypeScript 支持</strong>：类型推断更加准确</li>
        <li><strong>更小的打包体积</strong>：Tree-shaking 友好</li>
      </ul>
      
      <h3>基础用法</h3>
      <pre><code>&lt;script setup&gt;
import { ref, reactive, computed, onMounted } from 'vue'

// 响应式状态
const count = ref(0)
const state = reactive({ name: 'Vue' })

// 计算属性
const doubleCount = computed(() => count.value * 2)

// 生命周期钩子
onMounted(() => {
  console.log('组件已挂载')
})

// 方法
const increment = () => {
  count.value++
}
&lt;/script&gt;</code></pre>
      
      <h3>自定义 Hook</h3>
      <p>将通用逻辑提取到自定义 Hook 中：</p>
      <pre><code>// composables/useCounter.js
export function useCounter(initialValue = 0) {
  const count = ref(initialValue)
  const increment = () => count.value++
  const decrement = () => count.value--
  
  return { count, increment, decrement }
}</code></pre>
      
      <p>在组件中使用：</p>
      <pre><code>&lt;script setup&gt;
import { useCounter } from '@/composables/useCounter'

const { count, increment, decrement } = useCounter(10)
&lt;/script&gt;</code></pre>
      
      <p>这种模式让代码更加模块化和可测试。</p>
      
      <h3>与 Pinia 配合</h3>
      <p>组合式 API 与 Pinia 状态管理库完美配合，提供了现代化的状态管理解决方案。</p>
      
      <blockquote>
        <p>组合式 API 不是替代 Options API，而是提供了另一种更灵活的组织方式。你可以根据项目需求选择合适的方案。</p>
      </blockquote>
    `
  }
}

// 动态生成文章内容的函数（用于测试所有文章ID）
function generateMockArticle(id) {
  // 如果是预设的详细文章，直接返回
  if (detailedArticles[id]) {
    return detailedArticles[id]
  }
  
  // 为其他ID动态生成测试内容
  const titles = [
    '前端性能优化完全指南',
    'TypeScript 泛型深入理解', 
    'CSS 现代布局指南',
    'Pinia 状态管理最佳实践',
    'Nuxt3 服务端渲染入门',
    'TailwindCSS 实用技巧',
    'Vue Router 4 源码解析',
    '前端自动化测试入门',
    'Webpack vs Vite 对比分析',
    'JavaScript 设计模式实战',
    'Node.js 后端开发入门',
    'Three.js 3D 可视化',
    'Git 协作开发最佳实践',
    'ES2025 新特性一览',
    '前端安全防护指南',
    '微前端架构实践',
    'Docker 前端开发环境',
    'GraphQL 从入门到实践',
    'Vue3 响应式原理',
    'Chrome DevTools 调试技巧',
    'PWA 渐进式应用开发',
    'WebAssembly 实战',
    'Monorepo 管理大型项目',
    '响应式设计最佳实践',
    '前端工程化体系建设'
  ]
  
  const tagsList = [
    ['性能优化', '前端', 'Web'], 
    ['TypeScript', '泛型', '编程'],
    ['CSS', '布局', 'Flexbox', 'Grid'],
    ['Pinia', '状态管理', 'Vue'],
    ['Nuxt', 'SSR', 'SEO'],
    ['Tailwind', 'CSS', '原子化'],
    ['Vue Router', '路由', '前端'],
    ['测试', 'Vitest', '自动化'],
    ['Webpack', 'Vite', '构建工具'],
    ['设计模式', 'JavaScript', '编程'],
    ['Node.js', '后端', 'API'],
    ['Three.js', '3D', '可视化'],
    ['Git', '协作', '开发流程'],
    ['ES2025', 'JavaScript', '新特性'],
    ['安全', 'XSS', 'CSRF'],
    ['微前端', '架构', 'qiankun'],
    ['Docker', '容器化', '环境'],
    ['GraphQL', 'API', '数据查询'],
    ['响应式', 'Vue3', 'Proxy'],
    ['DevTools', '调试', 'Chrome'],
    ['PWA', '离线', '推送'],
    ['WebAssembly', 'Rust', '高性能'],
    ['Monorepo', 'pnpm', 'Turborepo'],
    ['响应式', '移动端', '桌面端'],
    ['工程化', 'CI/CD', '自动化']
  ]
  
  const summaries = [
    '从加载速度到运行时性能，全方位提升应用体验。',
    '泛型是 TypeScript 最强大的特性之一，掌握它能写出更灵活的代码。',
    '从 Flexbox 到 Grid，掌握现代 Web 布局的核心技术。',
    'Pinia 是 Vue 官方推荐的状态管理库，轻量且强大。',
    '使用 Nuxt3 轻松构建 SEO 友好的 Vue 应用。',
    '原子化 CSS 框架的最佳实践，让你写样式更高效。',
    '深入理解 Vue Router 的实现原理，掌握路由核心机制。',
    '使用 Vitest 和 Vue Test Utils 为应用保航。',
    '从构建原理到开发体验，全面对比两大构建工具。',
    '单例、工厂、观察者...经典设计模式在前端中的应用。',
    '使用 Express + MongoDB 快速搭建 RESTful API。',
    '在浏览器中创建令人惊艳的 3D 场景和动画。',
    '分支管理策略、Commit 规范、Code Review 流程。',
    '探索 JavaScript 最新特性，保持技术前沿。',
    'XSS、CSRF、SQL注入...常见安全问题及解决方案。',
    '使用 qiankun 实现大型应用的技术融合和独立部署。',
    '容器化开发环境，解决环境不一致的问题。',
    '相比 REST API，GraphQL 提供了更灵活的数据查询方式。',
    '深入理解 Proxy 和 Reflect 如何实现响应式系统。',
    '用好开发者工具，让 bug 无处遁形。',
    '让 Web 应用具备原生应用的离线缓存和推送能力。',
    '使用 Rust 编写高性能的 Web 模块。',
    '使用 pnpm workspace 或 Turborepo 管理多包项目。',
    '适配各种设备尺寸，提供一致的用户体验。',
    '从代码规范到自动化部署，建立完整的前端工程体系。'
  ]
  
  // 根据ID选择内容（循环使用）
  const index = (id - 1) % titles.length
  const title = titles[index]
  const tags = tagsList[index]
  const summary = summaries[index]
  
  // 生成日期（最近30天内）
  const date = new Date()
  date.setDate(date.getDate() - Math.floor(Math.random() * 30))
  const dateString = date.toISOString().split('T')[0]
  
  // 生成阅读量
  const views = Math.floor(Math.random() * 2000) + 100
  
  // 生成简单的内容
  const content = `
    <p>${summary}</p>
    
    <h2>主要内容</h2>
    <p>这是一篇关于<strong>${title}</strong>的技术文章，用于测试文章详情页的显示效果。</p>
    
    <h3>关键要点</h3>
    <ul>
      <li>这是第一个要点，展示了列表项的样式</li>
      <li>这是第二个要点，包含一些<strong>强调文本</strong></li>
      <li>这是第三个要点，可能包含<a href="#" onclick="return false;">链接样式</a></li>
    </ul>
    
    <blockquote>
      <p>这是一个引用块，用于展示引用样式的显示效果。引用块通常用于突出重要的观点或说明。</p>
    </blockquote>
    
    <p>文章内容到这里就结束了。这个页面目前使用预设内容进行测试，后续会对接真实的后端API获取数据。</p>
  `
  
  return {
    id: id,
    title: title,
    author: '观测笔记',
    date: dateString,
    views: views,
    tags: tags,
    content: content
  }
}

// TODO: 后续对接后端API的网络请求框架
// 这里预留了完整的API调用结构，只需要替换mockArticles为实际的API调用即可
async function loadArticle() {
  try {
    loading.value = true
    errorMessage.value = ''
    
    // 预留：实际的API调用位置
    // const { data, error } = await useArticleAPI().getArticle(articleId.value)
    // if (error.value) {
    //   throw new Error(error.value.friendlyMessage || '获取文章失败')
    // }
    // article.value = data.value
    
    // 当前使用mock数据 - 现在所有ID都能显示内容
    if (articleId.value) {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 600))
      article.value = generateMockArticle(articleId.value)
    } else {
      throw new Error('无效的文章ID')
    }
  } catch (error) {
    console.error('🐛 加载文章详情错误:', {
      articleId: articleId.value,
      error: error.message,
      timestamp: new Date().toISOString()
    })
    errorMessage.value = error.message
    article.value = null
  } finally {
    loading.value = false
  }
}

// 返回上一页
const handleBack = () => {
  router.push('/posts')
}

// 组件挂载时加载文章
onMounted(() => {
  if (articleId.value) {
    loadArticle()
  } else {
    loading.value = false
    errorMessage.value = '无效的文章ID'
  }
})

// 监听路由参数变化（支持同页面不同文章切换）
import { watch } from 'vue'
watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId && newId) {
    loadArticle()
  }
})
</script>

<style lang="scss" scoped>
.article-detail-wrapper {
  overflow-y: auto;
  background: var(--bg-white);
  scroll-behavior: smooth;
  position: relative;
  min-height: 100vh;
}

.back-button {
  position: fixed;
  top: 100px;
  left: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
  }
}

.content-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 120px 24px 80px;
}

.loading-state {
  .skeleton-title {
    height: 32px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    border-radius: 8px;
    margin-bottom: 16px;
    animation: loading 1.5s infinite;
  }
  
  .skeleton-meta {
    height: 20px;
    width: 200px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    border-radius: 4px;
    margin-bottom: 32px;
    animation: loading 1.5s infinite;
  }
  
  .skeleton-content {
    height: 20px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    border-radius: 4px;
    margin-bottom: 16px;
    animation: loading 1.5s infinite;
    
    &:nth-child(3) {
      width: 80%;
    }
    
    &:nth-child(4) {
      width: 60%;
    }
  }
}

.article-content {
  .article-title {
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 24px;
    color: var(--text-main);
  }
  
  .article-meta {
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
    
    .author, .date, .views {
      color: var(--text-secondary);
    }
    
    .dot {
      opacity: 0.6;
      margin: 0 8px;
    }
  }
  
  .article-body {
    line-height: 1.8;
    color: var(--text-main);
    font-size: 1.05rem;
    
    h2 {
      font-size: 1.8rem;
      margin: 40px 0 24px;
      font-weight: 600;
      color: var(--text-main);
    }
    
    h3 {
      font-size: 1.4rem;
      margin: 32px 0 20px;
      font-weight: 600;
      color: var(--text-main);
    }
    
    p {
      margin: 20px 0;
      text-align: justify;
    }
    
    ul {
      margin: 20px 0;
      padding-left: 24px;
      
      li {
        margin: 8px 0;
        line-height: 1.6;
      }
    }
    
    pre {
      background: var(--bg-code);
      border-radius: 8px;
      padding: 20px;
      margin: 24px 0;
      overflow-x: auto;
      font-family: 'Monaco', 'Consolas', monospace;
      font-size: 0.95rem;
      
      code {
        font-family: inherit;
        font-size: inherit;
      }
    }
    
    blockquote {
      border-left: 4px solid var(--primary-color);
      padding: 16px 24px;
      margin: 24px 0;
      background: var(--bg-quote);
      border-radius: 0 8px 8px 0;
      
      p {
        margin: 0;
        font-style: italic;
        color: var(--text-secondary);
      }
    }
    
    strong {
      font-weight: 600;
      color: var(--text-main);
    }
  }
  
  .article-tags {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
    
    .tag {
      display: inline-block;
      background: var(--bg-tag);
      color: var(--primary-color);
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 0.85rem;
      margin-right: 8px;
      margin-bottom: 8px;
      font-weight: 500;
    }
  }
}

.error-state {
  text-align: center;
  padding: 80px 24px;
  
  .error-icon {
    font-size: 3rem;
    margin-bottom: 24px;
    color: var(--error-color);
  }
  
  .error-message {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 24px;
    line-height: 1.5;
  }
  
  .retry-button {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s;
    
    &:hover {
      background: var(--primary-hover);
    }
  }
}

@keyframes loading {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

// 响应式设计
@media (max-width: 768px) {
  .content-container {
    padding: 100px 16px 60px;
  }
  
  .article-title {
    font-size: 1.8rem;
  }
  
  .article-body {
    font-size: 1rem;
    
    h2 {
      font-size: 1.5rem;
    }
    
    h3 {
      font-size: 1.2rem;
    }
  }
  
  .back-button {
    top: 80px;
    left: 16px;
    padding: 6px 12px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .article-title {
    font-size: 1.6rem;
  }
  
  .article-body {
    font-size: 0.95rem;
  }
}
</style>
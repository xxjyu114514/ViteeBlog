<template>
  <div 
    class="posts-immersive-wrapper" 
    @wheel="handleWheel"
  >
    <!-- 背景底层 -->
    <div class="hero-static">
      <div class="header-content">
        <h1 class="page-title">精选文章</h1>
        <p class="page-subtitle">发现优质内容，探索精彩世界</p>
      </div>
    </div>

    <div class="light-immersive-panel">
      <div class="responsive-container">
        
        <div class="list-section">
          <div class="articles-header">
            <h2 class="section-title">最新文章</h2>
            <p class="section-description">展示最新的6篇文章</p>
          </div>
          
          <div class="glass-main-card">
            
            <div class="items-stack">
              <!-- 动态文章列表 -->
              <div 
                v-if="loading"
                class="loading-state text-center"
              >
                <div class="loading-spinner"></div>
                <p>加载中...</p>
              </div>
              
              <div 
                v-else-if="error"
                class="error-state text-center"
              >
                <p class="error-message">{{ error }}</p>
                <button 
                  class="btn-secondary"
                  @click="loadArticles"
                >
                  重新加载
                </button>
              </div>
              
              <div 
                v-else-if="articles.length === 0"
                class="empty-state text-center"
              >
                <p>暂无文章</p>
              </div>
              
              <div 
                v-else
                class="glass-sub-card" 
                v-for="(article, index) in articles.slice(0, 6)" 
                :key="article.id"
                @click="goToArticle(article.id)"
              >
                <div class="card-internal">
                  <div class="text-info">
                    <span class="item-index">{{ String(index + 1).padStart(2, '0') }}</span>
                    <h3 class="item-title">{{ article.title || '无标题文章' }}</h3>
                  </div>
                  <span class="static-arrow">→</span>
                </div>
              </div>
            </div>

            <!-- "查看更多文章"按钮 - 使用sticky定位 -->
            <button 
              class="more-articles-btn"
              @click="navToSubList"
            >
              <span class="btn-text">查看更多文章</span>
            </button>
          </div>

          <div 
            class="more-trigger-area"
            @click="navToSubList"
          >
            <div class="more-content">
              <span class="more-text">了解更多</span>
              <span class="more-arrow">↗</span>
            </div>
          </div>

        </div>

        <div class="auth-section">
          <div class="glass-login-card">
            <header class="login-header">
              <div 
                v-if="!userStore.isAuthenticated" 
                class="user-avatar-glass"
              ></div>
              <div 
                v-else 
                class="user-info"
              >
                <span class="username">{{ userStore.user?.username || '用户' }}</span>
                <span class="role-badge">{{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}</span>
              </div>
              
              <h3 
                v-if="!userStore.isAuthenticated" 
                class="login-title"
              >LOGIN</h3>
              <h3 
                v-else 
                class="login-title"
              >欢迎回来</h3>
            </header>
            
            <div class="login-body">
              <button 
                v-if="!userStore.isAuthenticated"
                class="action-btn"
                @click="router.push('/login')"
              >
                立即登录
              </button>
              <button 
                v-else
                class="action-btn"
                @click="router.push('/personal')"
              >
                个人中心
              </button>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { useArticleAPI } from '@/composables/useArticleAPI'
import { useUserStore } from '@/stores/user'

// 滚轮导航逻辑
const { handleWheel } = usePrimaryPageWheel('posts-immersive')

// 路由和状态管理
const router = useRouter()
const userStore = useUserStore()

// 文章数据状态
const articles = ref([])
const loading = ref(false)
const error = ref(null)

// 初始化文章API
const { getPublicArticles } = useArticleAPI()

// 加载文章列表（只加载前6篇用于展示）
const loadArticles = async () => {
  loading.value = true
  error.value = null
  
  try {
    const result = await getPublicArticles(null, 1, 6)
    
    if (result.success) {
      articles.value = result.data.items || []
    } else {
      error.value = result.message || '获取文章列表失败'
    }
  } catch (err) {
    console.error('加载文章列表异常:', err)
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 跳转到文章详情页
const goToArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}

// 导航到完整文章列表
const navToSubList = () => {
  router.push('/posts')
}

// 组件挂载时加载文章
onMounted(() => {
  loadArticles()
})
</script>
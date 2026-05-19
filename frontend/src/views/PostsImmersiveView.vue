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
                <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
                <span class="role-badge">{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</span>
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
import { getPublicArticles } from '@/services/articleService'
import { useUserStore } from '@/stores/user'

const { handleWheel } = usePrimaryPageWheel('posts-immersive')
const router = useRouter()
const userStore = useUserStore()

const articles = ref([])
const loading = ref(false)
const error = ref(null)

const loadArticles = async () => {
  loading.value = true
  error.value = null
  try {
    const result = await getPublicArticles({ page: 1, size: 6 })
    if (result.success) {
      articles.value = result.data?.items || []
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

const goToArticle = (articleId) => router.push(`/article/${articleId}`)
const navToSubList = () => router.push('/posts')

onMounted(() => { loadArticles() })
</script>
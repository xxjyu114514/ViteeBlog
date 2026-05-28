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
          
          <!-- 玻璃面板容器（test_scss 组件） -->
          <div class="glass-panel panel-scroll">
            <!-- 左上角冰蓝装饰线由 .glass-panel 自带的 ::before 提供 -->
            
            <div class="panel-body">
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
                  class="btn btn-ghost"
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
              
              <!-- 文章列表项：使用 article-card 结构 -->
              <div 
                v-else
                class="article-card post-list-item" 
                v-for="(article, index) in articles.slice(0, 6)" 
                :key="article.id"
                @click="goToArticle(article.id)"
              >
                <div class="article-card__header">
                  <div class="meta-row">
                    <span class="item-index">{{ String(index + 1).padStart(2, '0') }}</span>
                    <h3 class="article-card__title">{{ article.title || '无标题文章' }}</h3>
                  </div>
                </div>
                <div class="article-card__footer">
                  <span class="static-arrow">→</span>
                </div>
              </div>
            </div>

            <!-- "查看更多文章"按钮 -->
            <div class="panel-footer">
              <button 
                class="btn btn-glass"
                @click="navToSubList"
              >
                <span>查看更多文章</span>
              </button>
            </div>
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
          <div class="glass-card">
            <div class="glass-card__title">
              <span v-if="!userStore.isAuthenticated">LOGIN</span>
              <span v-else>欢迎回来</span>
            </div>
            <div class="glass-card__body">
              <div class="user-mini">
                <div 
                  v-if="!userStore.isAuthenticated" 
                  class="avatar-placeholder"
                ></div>
                <div 
                  v-else 
                  class="user-info"
                >
                  <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
                  <span class="role-badge">{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</span>
                </div>
              </div>
              
              <button 
                v-if="!userStore.isAuthenticated"
                class="btn btn-primary btn-full"
                @click="router.push('/login')"
              >
                立即登录
              </button>
              <button 
                v-else
                class="btn btn-primary btn-full"
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
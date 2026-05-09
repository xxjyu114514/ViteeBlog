<template>
  <div 
    class="posts-immersive-wrapper" 
    @wheel="handleWheel"
  >
    <!-- 背景底层 -->
    <div class="hero-static">
      <div class="header-content">
        <h1 class="page-title">精选文章</h1>
      </div>
    </div>

    <div class="light-immersive-panel">
      <div class="responsive-container">
        
        <div class="list-section">
          <div class="glass-main-card">
            
            <div class="items-stack">
              <!-- 动态文章列表 -->
              <div 
                v-if="loading"
                class="loading-state text-center"
              >
                <div class="loading-spinner"></div>
                <p class="mt-20">正在加载文章...</p>
              </div>
              
              <div 
                v-else-if="error"
                class="error-state text-center"
              >
                <p class="error-message">{{ error }}</p>
                <button class="btn-secondary mt-20" @click="loadArticles">重新加载</button>
              </div>
              
              <div 
                v-else-if="articles.length === 0"
                class="empty-state text-center"
              >
                <p>暂无文章发布</p>
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
                    <span class="item-title">{{ article.title || '无标题文章' }}</span>
                  </div>
                  <div class="static-arrow">→</div>
                </div>
              </div>
            </div>

            <div class="more-trigger-area" @click.stop="navToSubList">
              <div class="more-content">
                <span class="more-text">了解更多</span>
                <span class="more-arrow">→</span>
              </div>
            </div>

          </div>
        </div>

        <div class="auth-section">
          <div class="glass-login-card">
            <div class="login-header">
              <div class="user-avatar-glass"></div>
              <span class="login-title">LOGIN</span>
            </div>
            <div class="login-body">
              <button class="action-btn" @click="handleLogin">立即登录</button>
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
const { handleWheel } = usePrimaryPageWheel('posts')

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

// 处理登录按钮点击
const handleLogin = () => {
  if (userStore.isAuthenticated) {
    router.push('/personal')
  } else {
    router.push('/login')
  }
}

// 组件挂载时加载文章
onMounted(() => {
  loadArticles()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/mixins' as *;

.posts-immersive-wrapper {
  .hero-static {
    height: 60vh;
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    
    .header-content {
      text-align: center;
      
      .page-title {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        margin: 0;
      }
    }
  }

  .light-immersive-panel {
    .responsive-container {
      display: flex;
      justify-content: space-between;
      padding: 40px 20px;
      max-width: 1200px;
      margin: 0 auto;
      
      .list-section {
        flex: 1;
        margin-right: 40px;
        
        .glass-main-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-radius: 20px;
          padding: 30px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.1);
          
          .items-stack {
            margin-bottom: 30px;
            
            .glass-sub-card {
              background: rgba(255, 255, 255, 0.8);
              border: 1px solid rgba(255, 255, 255, 0.5);
              border-radius: 15px;
              padding: 20px;
              margin-bottom: 15px;
              cursor: pointer;
              transition: transform 0.2s ease, box-shadow 0.2s ease;
              
              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                background: rgba(255, 255, 255, 0.9);
              }
              
              .card-internal {
                display: flex;
                justify-content: space-between;
                align-items: center;
                
                .text-info {
                  display: flex;
                  align-items: center;
                  gap: 15px;
                  
                  .item-index {
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: $color-primary;
                  }
                  
                  .item-title {
                    font-size: 1.1rem;
                    font-weight: 500;
                    color: #333;
                    max-width: 300px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                  }
                }
                
                .static-arrow {
                  font-size: 1.2rem;
                  color: #666;
                }
              }
            }
          }
          
          .more-trigger-area {
            background: linear-gradient(135deg, $color-primary 0%, #2563eb 100%);
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: transform 0.2s ease;
            
            &:hover {
              transform: translateY(-2px);
            }
            
            .more-content {
              display: flex;
              justify-content: space-between;
              align-items: center;
              color: white;
              
              .more-text {
                font-size: 1.1rem;
                font-weight: 500;
              }
              
              .more-arrow {
                font-size: 1.3rem;
              }
            }
          }
        }
      }
      
      .auth-section {
        width: 300px;
        
        .glass-login-card {
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-radius: 20px;
          padding: 30px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.1);
          
          .login-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            
            .user-avatar-glass {
              width: 40px;
              height: 40px;
              background: linear-gradient(135deg, $color-primary 0%, #2563eb 100%);
              border-radius: 50%;
            }
            
            .login-title {
              font-size: 1.2rem;
              font-weight: 600;
              color: #333;
            }
          }
          
          .login-body {
            .action-btn {
              width: 100%;
              padding: 12px;
              background: $color-primary;
              color: white;
              border: none;
              border-radius: 8px;
              font-size: 1rem;
              font-weight: 500;
              cursor: pointer;
              transition: background 0.2s ease;
              
              &:hover {
                background: $color-primary-hover;
              }
            }
          }
        }
      }
    }
  }

  // 加载和错误状态样式
  .loading-state,
  .error-state,
  .empty-state {
    padding: 2rem;
    text-align: center;
    
    .loading-spinner {
      width: 30px;
      height: 30px;
      border: 2px solid #f3f3f3;
      border-top: 2px solid $color-primary;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto;
    }
    
    .error-message {
      color: #e74c3c;
      font-size: 1rem;
      margin-bottom: 1rem;
    }
    
    p {
      font-size: 1rem;
      color: #666;
    }
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
}
</style>
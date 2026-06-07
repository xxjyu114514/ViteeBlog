<template>
  <div
    class="posts-immersive-wrapper"
    @wheel="handleWheel"
  >
    <!-- 上半部分：背景图区域 30vh -->
    <div class="hero-static">
      <!-- 页面切换动画用毛玻璃覆盖层（默认不可见） -->
      <div class="glass-overlay"></div>
      <div class="header-content">
        <h1 class="page-title">精选文章</h1>
        <p class="page-subtitle">发现优质内容，探索精彩世界</p>
      </div>
    </div>

    <!-- 下半部分：文章列表 70vh，纯色背景，内部自适应无滚动 -->
    <div class="list-panel">
      <div class="list-header">
        <h2 class="list-title">最新文章</h2>
      </div>
      <div class="panel-body" ref="panelBodyRef">
        <!-- 加载状态 -->
        <div v-if="loading" class="state-display">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="state-display">
          <p class="error-msg">{{ error }}</p>
          <button class="btn btn-ghost" @click="loadArticles">重新加载</button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="displayArticles.length === 0" class="state-display">
          <p>暂无文章</p>
        </div>

        <!-- 文章列表：动态数量，不溢出 -->
        <div v-else class="article-list">
          <div
            class="article-card"
            v-for="(article, index) in displayArticles"
            :key="article.id"
            @click="goToArticle(article.id)"
          >
            <div class="article-card__header">
              <div class="meta-row">
                <span class="item-index">{{ String(index + 1).padStart(2, '0') }}</span>
                <h3 class="article-card__title">{{ article.title || '无标题文章' }}</h3>
              </div>
            </div>
            <div v-if="article.summary" class="article-card__content">
              <p class="article-card__excerpt">{{ article.summary }}</p>
            </div>
            <div class="article-card__footer">
              <div class="article-card__stats">
                <span>❤️ {{ article.likeCount || 0 }}</span>
                <span>💬 {{ article.commentCount || 0 }}</span>
              </div>
              <span class="static-arrow">→</span>
            </div>
          </div>
        </div>
      </div>

      <div class="list-footer">
        <button class="btn btn-glass" @click="router.push('/posts')">查看更多文章</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { getPublicArticles } from '@/services/articleService'
import { formatDate } from '@/utils'

const { handleWheel } = usePrimaryPageWheel('posts-immersive')
const router = useRouter()

// ========== 文章数据 ==========
const articles = ref([])
const loading = ref(false)
const error = ref(null)

const loadArticles = async () => {
  loading.value = true
  error.value = null
  try {
    const result = await getPublicArticles({ page: 1, size: 50 })
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

// ========== 动态自适应文章数量 ==========
const panelBodyRef = ref(null)
const maxCount = ref(6)

const MIN_SLOT_HEIGHT = 120

const calcFitCount = () => {
  if (!panelBodyRef.value) return
  const h = panelBodyRef.value.clientHeight
  maxCount.value = Math.max(1, Math.floor(h / MIN_SLOT_HEIGHT))
}

let raf = null
const onResize = () => {
  if (raf) cancelAnimationFrame(raf)
  raf = requestAnimationFrame(calcFitCount)
}

const displayArticles = computed(() => {
  return articles.value.slice(0, maxCount.value)
})

const goToArticle = (articleId) => router.push(`/article/${articleId}`)

onMounted(() => {
  loadArticles()
  const unwatch = watch(articles, () => {
    nextTick(() => { calcFitCount(); unwatch() })
  })
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  if (raf) cancelAnimationFrame(raf)
})
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/assets/styles/variables' as *;

.posts-immersive-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: $bg-dark;
}

/* ===== 上半部分：背景图区域 30vh ===== */
.hero-static {
  height: 30vh;
  min-height: 200px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  background: $bg-dark url(#{$img-posts-bg}) center / cover no-repeat;
  background-position-y: 30%;

  // 页面切换动画用毛玻璃覆盖层（默认 opacity:0 不可见）
  .glass-overlay {
    position: absolute;
    inset: 0;
    z-index: 1;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0;
    pointer-events: none;
  }

  .header-content {
    text-align: left;
    padding-left: 40px;
    width: 100%;

    .page-title {
      font-size: 2.5rem;
      font-weight: 700;
      color: $text-primary;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
      margin: 0;
    }

    .page-subtitle {
      font-size: 1.1rem;
      color: $text-primary;
      margin-top: 8px;
    }
  }
}

/* ===== 下半部分：文章列表区 ===== */
.list-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: $bg-base;
  border-top: 1px solid rgba(255, 255, 255, 0.06);

  .list-header {
    flex-shrink: 0;
    padding: 20px 24px 0;

    .list-title {
      font-size: 1.3rem;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }

  .panel-body {
    flex: 1;
    overflow: hidden;
    padding: 16px 24px 0;
  }

  .list-footer {
    flex-shrink: 0;
    padding: 16px 24px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }
}

/* ===== 文章卡片容器（60vw 居中） ===== */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 60vw;
  margin: 0 auto;
}

/* ===== 文章卡片 ===== */
.article-card {
  background: $bg-surface;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: $space-lg;
  position: relative;
  cursor: pointer;
  transition: border-color $transition-base, box-shadow $transition-base;

  &::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    background: linear-gradient(to right,
      transparent 0%, rgba($color-primary, 0.06) 50%, rgba($color-primary, 0.15) 100%);
    opacity: 0;
    transition: opacity $transition-base;
    pointer-events: none;
    z-index: 1;
  }

  &:hover::before { opacity: 1; }
  &:hover {
    border-color: rgba($color-primary, 0.2);
    box-shadow: $glow-brand;
  }

  .article-card__header {
    position: relative;
    z-index: 2;

    .meta-row {
      display: flex;
      align-items: center;
      gap: 16px;

      .item-index {
        font-size: 1.2rem;
        font-weight: 600;
        color: $color-primary;
        flex-shrink: 0;
      }

      .article-card__title {
        font-size: 1.1rem;
        font-weight: 600;
        color: $text-primary;
        margin: 0;
        line-height: 1.3;
      }
    }
  }

  .article-card__content {
    position: relative;
    z-index: 2;
    margin: 8px 0;
    color: $text-secondary;
    line-height: 1.6;
  }

  .article-card__excerpt {
    font-size: 0.85rem;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-card__footer {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .article-card__stats {
    display: flex;
    gap: 16px;
    color: $text-tertiary;
    font-size: 0.8rem;
  }

  .static-arrow {
    font-size: 1.2rem;
    color: $text-tertiary;
  }
}

/* ===== 状态显示 ===== */
.state-display {
  padding: 2rem;
  text-align: center;

  .loading-spinner {
    width: 30px; height: 30px;
    border: 2px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid $color-primary;
    border-radius: 50% !important;
    animation: spin 1s linear infinite;
    margin: 0 auto 12px;
  }

  .error-msg { color: $color-error; font-size: 1rem; margin-bottom: 1rem; }
  p { font-size: 1rem; color: $text-secondary; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .hero-static {
    min-height: 160px;
    .header-content {
      padding-left: 20px;
      .page-title { font-size: 1.8rem; }
      .page-subtitle { font-size: 0.95rem; }
    }
  }

  .list-panel {
    .panel-body { padding: 12px 16px 0; }
    .list-footer { padding: 12px 16px; }
  }

  .article-card { padding: $space-md; }
  .article-list { max-width: 90vw; }
}
</style>

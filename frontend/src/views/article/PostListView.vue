<template>
  <div class="page-wrapper-base padding-page post-page-wrapper">
    <div class="back-button" @click="router.push('/posts-immersive')">
      ← 返回
    </div>

    <!-- 可滚动内容区：背景图 + 毛玻璃 -->
    <div class="content-scroller">
      <div class="glass-background">
        <!-- 外层卡片容器（article-card 样式） -->
        <div class="article-card outer-card">
          <div class="article-card__header">
            <h2 class="article-card__title">全部文章</h2>
            <div class="tab-header">
              <button
                :class="{ active: currentTab === 'latest' }"
                @click="currentTab = 'latest'"
              >最新文章</button>
              <button
                :class="{ active: currentTab === 'hot' }"
                @click="currentTab = 'hot'"
              >热门文章</button>
              <button
                class="refresh-btn"
                @click="loadArticles"
                :disabled="loading"
              >🔄 刷新</button>
            </div>
          </div>

          <div class="article-card__content">
            <div v-if="loading" class="state-display">
              <div class="loading-spinner"></div>
              <p>加载文章列表中...</p>
            </div>

            <div v-else-if="error" class="state-display">
              <p class="error-msg">{{ error }}</p>
              <button class="btn btn-ghost" @click="loadArticles">重新加载</button>
            </div>

            <div v-else-if="filteredArticles.length === 0" class="state-display">
              <p>暂无文章</p>
            </div>

            <div v-else class="inner-list">
              <div
                class="article-card inner-card"
                v-for="article in filteredArticles"
                :key="article.id"
                @click="goToArticle(article.id)"
              >
                <div class="article-card__header">
                  <h3 class="article-card__title">
                    <a href="javascript:void(0)">{{ article.title || '无标题文章' }}</a>
                  </h3>
                  <div class="article-card__meta">
                    <span>作者</span>
                    <span>{{ formatDate(article.publishedAt) }}</span>
                    <span>· {{ article.viewCount || 0 }} 阅读</span>
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
                  <span class="article-card__tag">阅读全文 →</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPublicArticles } from '@/services/articleService'
import { formatDate } from '@/utils'

const router = useRouter()
const currentTab = ref('latest')
const articles = ref([])
const loading = ref(true)
const error = ref(null)

const loadArticles = async () => {
  loading.value = true
  error.value = null
  const result = await getPublicArticles()
  if (result.success) {
    articles.value = result.data?.items || []
  } else {
    error.value = result.message
  }
  loading.value = false
}

const filteredArticles = computed(() => {
  if (currentTab.value === 'hot') {
    return [...articles.value].sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
  }
  return articles.value
})

const goToArticle = (articleId) => router.push(`/article/${articleId}`)

onMounted(() => { loadArticles() })
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/assets/styles/variables' as *;

.post-page-wrapper {
  position: relative;
}

.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: $text-secondary;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  &:hover {
    color: $text-primary;
    border-color: rgba($color-primary, 0.3);
  }
}

.content-scroller {
  min-height: 100vh;
  padding: 90px 24px 40px;
}

/* ===== 毛玻璃背景层 ===== */
.glass-background {
  position: relative;
  width: 100%;
  min-height: calc(100vh - 130px);
  max-width: 900px;
  margin: 0 auto;

  &::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: $bg-dark url(#{$img-posts-list-bg}) center / cover no-repeat;
    background-position-y: 30%;
    filter: blur(8px) brightness(0.5);
    z-index: -1;
  }
}

/* ===== 外层卡片容器 ===== */
.outer-card {
  background: rgba($bg-surface, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: $space-lg;
  position: relative;
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
  &:hover { border-color: rgba($color-primary, 0.2); }

  .article-card__header { position: relative; z-index: 2; margin-bottom: $space-sm; }
  .article-card__content { position: relative; z-index: 2; }
}

/* ===== Tab 切换 ===== */
.tab-header {
  display: flex;
  gap: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 16px;
  padding-bottom: 4px;

  button {
    padding: 10px 8px;
    background: none;
    border: none;
    font-size: 0.95rem;
    color: $text-secondary;
    cursor: pointer;
    position: relative;
    transition: color 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover { color: $text-primary; }

    &.active {
      color: $color-primary;
      font-weight: 600;
      &::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 100%;
        height: 2.5px;
        background: $color-primary;
      }
    }

    &.refresh-btn {
      margin-left: auto;
      padding: 10px 12px;
      font-size: 0.85rem;
      color: $color-primary;
      &:disabled { opacity: 0.5; cursor: not-allowed; }
    }
  }
}

/* ===== 内层卡片列表 ===== */
.inner-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.inner-card {
  background: $bg-surface;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: $space-md;
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

  .article-card__header { position: relative; z-index: 2; margin-bottom: 8px; }

  .article-card__title {
    font-size: 1.1rem;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
    line-height: 1.3;
    a { color: inherit; text-decoration: none; &:hover { color: $color-primary; } }
  }

  .article-card__meta {
    display: flex;
    align-items: center;
    gap: 12px;
    color: $text-secondary;
    font-size: 0.8rem;
    margin-top: 6px;
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
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .article-card__stats {
    display: flex;
    gap: 16px;
    color: $text-tertiary;
    font-size: 0.8rem;
  }

  .article-card__tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: $bg-elevated;
    padding: 4px 10px;
    font-size: 0.75rem;
    color: $text-secondary;
    text-decoration: none;
    &:hover { color: $color-primary; background: $bg-hover; }
  }
}

/* ===== 状态显示 ===== */
.state-display {
  padding: 40px 0;
  text-align: center;

  .loading-spinner {
    width: 32px; height: 32px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top: 3px solid $color-primary;
    border-radius: 50% !important;
    animation: spin 1s linear infinite;
    margin: 0 auto 12px;
  }

  .error-msg { color: $color-error; margin-bottom: 12px; }
  p { color: $text-secondary; font-size: 1rem; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .content-scroller { padding: 80px 12px 24px; }
  .outer-card { padding: $space-md; }

  .tab-header {
    gap: 12px;
    button { font-size: 0.85rem; padding: 8px 4px; }
  }

  .inner-card { padding: $space-sm; }
}
</style>

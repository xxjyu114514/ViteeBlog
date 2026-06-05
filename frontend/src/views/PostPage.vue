<template>
  <div
    class="post-page"
    :class="[currentMode]"
    @wheel="onWheel"
  >
    <!-- ===== A: 背景图区域 ===== -->
    <div class="bg-section">
      <!-- 毛玻璃覆盖层（posts 模式下渐显，由 CSS transition 驱动） -->
      <div class="glass-overlay"></div>

      <div class="header-content">
        <h1 class="page-title">精选文章</h1>
        <p class="page-subtitle">发现优质内容，探索精彩世界</p>
      </div>
    </div>

    <!-- ===== B: 文章列表区域 ===== -->
    <div class="list-section">
      <div v-show="isImmersive" class="list-header">
        <h2 class="list-title">最新文章</h2>
      </div>

      <!-- posts 模式下的 tab 切换 -->
      <div v-show="!isImmersive" class="tab-header">
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

      <div class="list-body" ref="listBodyRef">
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

        <!-- 文章卡片列表 -->
        <div v-else class="article-list">
          <div
            v-for="(article, index) in displayArticles"
            :key="article.id"
            class="article-card"
            :class="{ 'is-immersive-item': isImmersive }"
            @click="goToArticle(article.id)"
          >
            <div class="article-card__header">
              <div v-if="isImmersive" class="meta-row">
                <span class="item-index">{{ String(index + 1).padStart(2, '0') }}</span>
                <h3 class="article-card__title">{{ article.title || '无标题文章' }}</h3>
              </div>
              <template v-else>
                <h3 class="article-card__title">
                  <a href="javascript:void(0)">{{ article.title || '无标题文章' }}</a>
                </h3>
                <div class="article-card__meta">
                  <span>作者</span>
                  <span>{{ formatDate(article.publishedAt) }}</span>
                  <span>· {{ article.viewCount || 0 }} 阅读</span>
                </div>
              </template>
            </div>

            <div v-if="article.summary" class="article-card__content">
              <p class="article-card__excerpt">{{ article.summary }}</p>
            </div>

            <div class="article-card__footer">
              <div class="article-card__stats">
                <span>❤️ {{ article.likeCount || 0 }}</span>
                <span>💬 {{ article.commentCount || 0 }}</span>
              </div>
              <span v-if="isImmersive" class="static-arrow">→</span>
              <span v-else class="article-card__tag">阅读全文 →</span>
            </div>
          </div>
        </div>
      </div>

      <!-- immersive 模式底部按钮 -->
      <div v-show="isImmersive" class="list-footer">
        <button class="btn btn-glass" @click="switchToPostsMode">查看更多文章</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { getPublicArticles } from '@/services/articleService'
import { formatDate } from '@/utils'

const router = useRouter()
const route = useRoute()

// ========== 模式判断 ==========
const isImmersive = computed(() => route.name === 'posts-immersive')
const currentMode = computed(() => isImmersive.value ? 'mode-immersive' : 'mode-posts')

// ========== 滚轮导航（仅 immersive 模式） ==========
const { handleWheel } = usePrimaryPageWheel('posts-immersive')

/** 始终绑定的 wheel 拦截器，仅在 immersive 模式执行导航并阻止滚动 */
const onWheel = (e) => {
  if (isImmersive.value) {
    e.preventDefault()
    handleWheel(e)
  }
}

// ========== 文章数据 ==========
const articles = ref([])
const loading = ref(false)
const error = ref(null)
const currentTab = ref('latest')

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

// ========== 动态自适应文章数量（仅 immersive 模式） ==========
const listBodyRef = ref(null)
const immersiveMaxCount = ref(6)
const MIN_SLOT_HEIGHT = 120

const calcImmersiveCount = () => {
  if (!isImmersive.value || !listBodyRef.value) return
  const h = listBodyRef.value.clientHeight
  immersiveMaxCount.value = Math.max(1, Math.floor(h / MIN_SLOT_HEIGHT))
}

let resizeRaf = null
const onResize = () => {
  if (resizeRaf) cancelAnimationFrame(resizeRaf)
  resizeRaf = requestAnimationFrame(calcImmersiveCount)
}

watch(isImmersive, (val) => {
  if (val) nextTick(calcImmersiveCount)
})

// ========== 当前模式显示的条目 ==========
const displayArticles = computed(() => {
  let list = articles.value
  if (!isImmersive.value && currentTab.value === 'hot') {
    list = [...articles.value].sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
  }
  if (isImmersive.value) {
    return list.slice(0, immersiveMaxCount.value)
  }
  return list
})

const goToArticle = (articleId) => router.push(`/article/${articleId}`)

const switchToPostsMode = () => {
  router.push('/posts')
}

onMounted(() => {
  loadArticles()
  const unwatch = watch(articles, () => {
    nextTick(() => { calcImmersiveCount(); unwatch() })
  })
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  if (resizeRaf) cancelAnimationFrame(resizeRaf)
})
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/assets/styles/variables' as *;

/* ============================================================
   基础容器 — 固定 100vh，不可滚动
   ============================================================ */
.post-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden !important;
  background: $bg-dark;
}

/* 沉浸式模式下 .list-body 禁止滚动条（内容由动态计算适配） */
.mode-immersive .list-body {
  overflow-y: hidden !important;
}

/* ============================================================
   A: 背景图区域
   沉浸式: height 30vh
   posts:   height 100vh + 毛玻璃覆盖层渐显
   ============================================================ */
.bg-section {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 30vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  background: $bg-dark url('@/assets/hero-bg.webp') center / cover no-repeat;
  background-position-y: 30%;
  transition: height 0.5s ease-in-out;
  z-index: 1;

  .glass-overlay {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0;
    transition: opacity 0.5s ease-in-out;
    pointer-events: none;
  }

  .header-content {
    position: relative;
    z-index: 2;
    text-align: left;
    padding-left: 40px;
    width: 100%;
    transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;

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

/* posts 模式：背景图扩展到全屏 + 毛玻璃渐显 + 标题淡出上移 */
.mode-posts .bg-section {
  height: 100vh;

  .glass-overlay { opacity: 0.5; }
  .header-content { opacity: 0; transform: translateY(-20px); }
}

/* ============================================================
   B: 文章列表区域
   沉浸式: top 30vh, 纯色背景, 全宽
   posts:   top 0, 毛玻璃背景, 全宽（预留导航栏）
   ============================================================ */
.list-section {
  position: absolute;
  top: 30vh;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: top 0.5s ease-in-out, background 0.5s ease-in-out,
              backdrop-filter 0.5s ease-in-out;
  z-index: 2;

  background: $bg-base;
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);

  .list-header {
    flex-shrink: 0;
    padding: 20px 24px 0;
    transition: opacity 0.35s ease-in-out;
    .list-title { font-size: 1.3rem; font-weight: 600; color: $text-primary; margin: 0; }
  }

  .list-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px 0;
  }

  .list-footer {
    flex-shrink: 0;
    padding: 16px 24px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    transition: opacity 0.35s ease-in-out;
  }
}

/* posts 模式：覆盖全屏 + 毛玻璃 + 导航栏间距 */
.mode-posts .list-section {
  top: 0;
  padding-top: 90px;
  background: rgba($bg-base, 0.75);
  backdrop-filter: blur(16px) saturate(1.2);
  -webkit-backdrop-filter: blur(16px) saturate(1.2);
}

/* 双向文本渐入渐出：header/tab/footer 交叉淡变 */
.tab-header {
  transition: opacity 0.35s ease-in-out;
}

.mode-posts .list-header,
.mode-posts .list-footer {
  opacity: 0;
}

.mode-immersive .tab-header {
  opacity: 0;
}

/* posts 模式：主体内容渐入 */
@keyframes postsContentFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.mode-posts .list-body {
  animation: postsContentFadeIn 0.5s ease-in-out 0.15s both;
}

/* ============================================================
   文章卡片容器 — 宽度约束（CSS transition 驱动）
   沉浸式: 卡片区宽 60vw
   posts:  卡片区宽 80vw
   ============================================================ */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 60vw;
  margin: 0 auto;
  transition: max-width 0.5s ease-in-out;
}

.mode-posts .article-list {
  max-width: 80vw;
}

/* ============================================================
   Tab 切换（仅 posts 模式）
   ============================================================ */
.tab-header {
  flex-shrink: 0;
  display: flex;
  gap: 20px;
  padding: 20px 24px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

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
      color: $color-primary; font-weight: 600;
      &::after {
        content: '';
        position: absolute;
        bottom: -5px; left: 0;
        width: 100%; height: 2.5px;
        background: $color-primary;
      }
    }

    &.refresh-btn {
      margin-left: auto; padding: 10px 12px; font-size: 0.85rem; color: $color-primary;
      &:disabled { opacity: 0.5; cursor: not-allowed; }
    }
  }
}

/* ============================================================
   文章卡片 — 复用 test_scss.vue 的 article-card 样式
   ============================================================ */
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
  &:hover { border-color: rgba($color-primary, 0.2); box-shadow: $glow-brand; }

  .article-card__header { position: relative; z-index: 2; margin-bottom: $space-sm; }

  .article-card__title {
    font-size: 1.1rem; font-weight: 600; color: $text-primary; margin: 0; line-height: 1.3;
    a { color: inherit; text-decoration: none; &:hover { color: $color-primary; } }
  }

  .article-card__meta {
    display: flex; align-items: center; gap: 12px;
    color: $text-secondary; font-size: 0.8rem; margin-top: 6px;
  }

  .article-card__content {
    position: relative; z-index: 2;
    margin: $space-md 0; color: $text-secondary; line-height: 1.6;
  }

  .article-card__excerpt {
    font-size: 0.85rem; margin: 0;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }

  .article-card__footer {
    position: relative; z-index: 2;
    display: flex; justify-content: space-between; align-items: center;
    margin-top: $space-md; padding-top: $space-sm;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .article-card__stats { display: flex; gap: 16px; color: $text-tertiary; font-size: 0.8rem; }

  .article-card__tag {
    display: inline-flex; align-items: center; gap: 4px;
    background: $bg-elevated; padding: 4px 10px; font-size: 0.75rem;
    color: $text-secondary; text-decoration: none;
    &:hover { color: $color-primary; background: $bg-hover; }
  }
}

/* immersive 模式列表项简化布局 */
.article-card.is-immersive-item {
  .meta-row {
    display: flex; align-items: center; gap: 16px;
    .item-index { font-size: 1.2rem; font-weight: 600; color: $color-primary; flex-shrink: 0; }
    .article-card__title { margin: 0; }
  }
  .article-card__header { margin-bottom: 0; }
  .article-card__content { margin: 8px 0; }
  .article-card__footer { margin-top: 8px; padding-top: 6px; }
  .static-arrow { font-size: 1.2rem; color: $text-tertiary; }
}

/* ============================================================
   状态显示
   ============================================================ */
.state-display {
  padding: 2rem; text-align: center;

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

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
  .bg-section {
    .header-content {
      padding-left: 20px;
      .page-title { font-size: 1.8rem; }
      .page-subtitle { font-size: 0.95rem; }
    }
  }

  .list-section {
    .list-body { padding: 12px 16px 0; }
    .list-footer { padding: 12px 16px; }
  }

  .article-card { padding: $space-md; }

  .tab-header {
    gap: 12px; padding: 16px 16px 0;
    button { font-size: 0.85rem; padding: 8px 4px; }
  }

  .article-list { max-width: 90vw; }
  .mode-posts .article-list { max-width: 100vw; }
}
</style>

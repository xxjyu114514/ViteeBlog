<template>
  <div class="post-page" :class="[currentMode]" @wheel="onWheel">

    <!-- ============================================================
         MODE: immersive — PanelNews 1:1
         ============================================================ -->
    <div v-show="isImmersive" class="panel-news">

      <!-- 轮播 Source: ._4c6251ec top:9.5, right:14.75, w:83.125, h:46.875 -->
      <div class="news-swiper-wrap">
        <div class="news-carousel" ref="carouselRef" @scroll.passive="onCarouselScroll">
          <div class="news-carousel-inner">
            <div
              v-for="(article, idx) in hotArticles"
              :key="article.id"
              class="news-carousel-slide"
              @click="goToArticle(article.id)"
            >
              <div class="news-slide-block" :style="{ background: getCoverGradient(article, idx) }">
                <span class="slide-watermark">{{ article.title?.charAt(0) || '文' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 进度条 Source: ._84945841 top:56.375, right:0, w:61, h:.5 -->
      <div class="news-scrollbar-wrap">
        <div class="news-scrollbar-track">
          <div class="news-scrollbar-thumb" :style="progressStyle"></div>
        </div>
      </div>

      <!-- Info 区 Source: ._f00913a8 left:0, top:9.5, w:34.375, h:46.75 -->
      <div class="news-info">
        <div class="news-info-bg"></div>
        <div class="news-info-inner">

          <!-- tabs Source: ._8419bfdd -->
          <div class="news-tabs">
            <div class="news-tab active">
              <span>最新文章</span>
              <svg viewBox="0 0 7 15"><path d="M0.5,0.5 L6.5,7.5 L0.5,14.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
            </div>
          </div>

          <!-- 文章列表 Source: ._0882dfb6 -->
          <div class="news-list">
            <a
              v-for="article in latestArticles"
              :key="article.id"
              class="news-item"
              @click.prevent="goToArticle(article.id)"
            >
              <span class="tag">{{ article.category?.categoryName || article.category?.name || '文章' }}</span>
              <span class="info">
                <div class="date">{{ formatPanelDate(article.createdAt) }}</div>
                <div class="title">{{ article.title }}</div>
              </span>
            </a>
            <!-- READ MORE Source: ._b9c239f0 -->
            <a class="news-more-btn" @click.prevent="switchToPostsMode">
              <span>READ MORE</span>
              <svg viewBox="0 0 7 15"><path d="M0.5,0.5 L6.5,7.5 L0.5,14.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
            </a>
          </div>

          <!-- 轮播文章信息 Source: ._e2f809d4 left:3.875, bottom:-1.875, w:26.5 -->
          <div class="news-main">
            <div class="news-main-date">{{ formatPanelDate(currentHotArticle?.createdAt) }}</div>
            <div class="news-main-title">{{ currentHotArticle?.title || '暂无文章' }}</div>
            <div class="news-main-url">VITEEBLOG // ARTICLE</div>
            <!-- Source: ._6b41422f w:14.375, h:3.75 -->
            <a class="news-main-btn" @click.prevent="currentHotArticle && goToArticle(currentHotArticle.id)">
              <span>
                <div class="btn-main">阅读全文</div>
                <div class="btn-sub">READ MORE</div>
              </span>
              <svg viewBox="0 0 7 15"><path d="M0.5,0.5 L6.5,7.5 L0.5,14.5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
            </a>
          </div>
        </div>

        <!-- 水印 Source: ._ddfc4ee5 top:100%, left:9, font:7rem -->
        <div class="news-label"><span>BREAKING NEWS</span></div>
      </div>
    </div>

    <!-- ============================================================
         MODE: posts — 现有卡片列表（保留）
         ============================================================ -->
    <div v-show="!isImmersive" class="panel-posts">
      <div class="bg-section">
        <div class="glass-overlay"></div>
        <div class="header-content">
          <h1 class="page-title">精选文章</h1>
          <p class="page-subtitle">发现优质内容，探索精彩世界</p>
        </div>
      </div>
      <div class="list-section">
        <div class="tab-header">
          <button :class="{ active: currentTab === 'latest' }" @click="currentTab = 'latest'">最新文章</button>
          <button :class="{ active: currentTab === 'hot' }" @click="currentTab = 'hot'">热门文章</button>
          <button class="refresh-btn" @click="loadArticles" :disabled="loading">🔄 刷新</button>
        </div>
        <div class="list-body" ref="listBodyRef">
          <div v-if="loading" class="state-display">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          <div v-else-if="error" class="state-display">
            <p class="error-msg">{{ error }}</p>
            <button class="btn btn-ghost" @click="loadArticles">重新加载</button>
          </div>
          <div v-else-if="displayArticles.length === 0" class="state-display">
            <p>暂无文章</p>
          </div>
          <div v-else class="article-list">
            <ArticleCard
              v-for="(article, index) in displayArticles"
              :key="article.id"
              :article="article"
              :index="index"
              :immersive="false"
              @click="goToArticle"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { getPublicArticles } from '@/services/articleService'
import ArticleCard from '@/components/ArticleCard.vue'

const router = useRouter()
const route = useRoute()

// ========== 模式判断 ==========
const isImmersive = computed(() => route.name === 'posts-immersive')
const currentMode = computed(() => isImmersive.value ? 'mode-immersive' : 'mode-posts')

// ========== 滚轮导航（仅 immersive） ==========
const { handleWheel } = usePrimaryPageWheel('posts-immersive')
const onWheel = (e) => { if (isImmersive.value) { e.preventDefault(); handleWheel(e) } }

// ========== 文章数据 ==========
const articles = ref([])
const loading = ref(false)
const error = ref(null)

const loadArticles = async () => {
  loading.value = true; error.value = null
  try {
    const result = await getPublicArticles({ page: 1, size: 50 })
    if (result.success) { articles.value = result.data?.items || [] }
    else { error.value = result.message || '获取文章列表失败' }
  } catch (err) {
    console.error('加载文章列表异常:', err)
    error.value = '网络错误，请稍后重试'
  } finally { loading.value = false }
}

// ========== 轮播：热门 top4 ==========
const hotArticles = computed(() =>
  [...articles.value].sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0)).slice(0, 4)
)
const carouselRef = ref(null)
const currentCarouselIdx = ref(0)
const currentHotArticle = computed(() => hotArticles.value[currentCarouselIdx.value] || hotArticles.value[0])

const progressStyle = computed(() => {
  const count = hotArticles.value.length || 1
  return { width: (100 / count) + '%', transform: `translate3d(${currentCarouselIdx.value * 100}%,0,0)` }
})

const onCarouselScroll = (e) => {
  const el = e.target; const w = el.offsetWidth
  if (!w) return
  const idx = Math.round(el.scrollLeft / w)
  if (idx !== currentCarouselIdx.value && idx >= 0 && idx < hotArticles.value.length) {
    currentCarouselIdx.value = idx
  }
}

let autoTimer = null
const startAutoPlay = () => {
  stopAutoPlay()
  autoTimer = setInterval(() => {
    if (hotArticles.value.length <= 1) return
    const next = (currentCarouselIdx.value + 1) % hotArticles.value.length
    currentCarouselIdx.value = next
    const el = carouselRef.value
    if (el) el.scrollTo({ left: next * el.offsetWidth, behavior: 'smooth' })
  }, 4000)
}
const stopAutoPlay = () => { if (autoTimer) { clearInterval(autoTimer); autoTimer = null } }

// ========== 封面渐变 ==========
const coverHues = [200, 260, 320, 160, 30, 80, 140, 210, 280, 340]
const getCoverGradient = (article, idx) => {
  const str = (article.title || '') + String(idx)
  const hash = str.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  const hue = coverHues[hash % coverHues.length]
  const hue2 = (hue + 25) % 360
  return `linear-gradient(135deg, hsl(${hue}, 35%, 18%) 0%, hsl(${hue2}, 30%, 8%) 60%, hsl(${hue}, 40%, 5%) 100%)`
}

// ========== 最新文章列表（info 区） ==========
const latestArticles = computed(() => articles.value.slice(0, 6))

const formatPanelDate = (dateStr) => {
  if (!dateStr) return '---- // -- / --'
  const d = new Date(dateStr)
  return `${d.getFullYear()} // ${String(d.getMonth() + 1).padStart(2, '0')} / ${String(d.getDate()).padStart(2, '0')}`
}

// ========== posts 模式 ==========
const currentTab = ref('latest')
const listBodyRef = ref(null)
const displayArticles = computed(() => {
  if (currentTab.value === 'hot')
    return [...articles.value].sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
  return articles.value
})

const goToArticle = (articleOrId) => {
  const id = typeof articleOrId === 'object' ? articleOrId.id : articleOrId
  if (id) router.push(`/article/${id}`)
}
const switchToPostsMode = () => router.push('/posts')

// ========== 生命周期 ==========
onMounted(() => {
  loadArticles()
  applyFontSize()
  window.addEventListener('resize', applyFontSize)
  watch(articles, (val) => { if (val.length > 0) nextTick(startAutoPlay) }, { once: true })
})
onBeforeUnmount(() => {
  stopAutoPlay()
  restoreFontSize()
  window.removeEventListener('resize', applyFontSize)
})

// ========== Arknights 动态 font-size（1:1 移植 app.js initFontSize） ==========
let savedFs = null

function applyFontSize() {
  if (savedFs === null) {
    savedFs = document.documentElement.style.fontSize || ''
  }
  var base = 16
  var iw = window.innerWidth, ih = window.innerHeight
  var fs = base
  if (ih >= iw) {
    fs *= (iw / ih > 750 / 1334) ? (ih / 1334) : (iw / 750)
  } else {
    fs *= (iw / ih > 1920 / 1080) ? (ih / 1080) : (iw / 1920)
  }
  document.documentElement.style.fontSize = fs + 'px'
}

function restoreFontSize() {
  if (savedFs !== null) {
    document.documentElement.style.fontSize = savedFs
    savedFs = null
  }
}
</script>

<style lang="scss" scoped>
@use 'sass:color';
@use '@/assets/styles/variables' as *;

/* ============================================================
   基础容器
   ============================================================ */
.post-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden !important;
  background: #111;
}

/* ============================================================
   MODE: immersive — PanelNews 1:1 移植
   CSS 使用 Arknights 源站 rem 值
   html font-size 由 JS applyFontSize 动态缩放
   ============================================================ */

/* Source: ._446c7f49 */
.panel-news { background: #111; position: absolute; inset: 0; }

/* ----- 轮播 Source: ._4c6251ec ----- */
.news-swiper-wrap {
  position: absolute;
  top: 9.5rem;
  right: 14.75rem;
  width: 83.125rem;
  height: 46.875rem;
  -webkit-mask: linear-gradient(90deg, transparent, #fff 20%);
  mask: linear-gradient(90deg, transparent, #fff 20%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.news-carousel { width:100%; height:100%; overflow-x:auto; overflow-y:hidden; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch; scrollbar-width:none; }
.news-carousel::-webkit-scrollbar { display:none; }
.news-carousel-inner { display:flex; height:100%; }
.news-carousel-slide { flex:0 0 100%; height:100%; scroll-snap-align:start; display:flex; align-items:center; justify-content:center; cursor:pointer; }
.news-slide-block { width:100%; height:100%; object-fit:cover; display:flex; align-items:center; justify-content:center; }
.news-slide-block .slide-watermark { font-size:8rem; font-weight:900; color:rgba(255,255,255,0.06); font-family:'Arial Black','Impact',sans-serif; pointer-events:none; user-select:none; }

/* ----- 进度条 Source: ._84945841 ----- */
.news-scrollbar-wrap { position:absolute; z-index:4; top:56.375rem; right:0; width:61rem; height:.5rem; }
.news-scrollbar-wrap::before { content:''; position:absolute; top:0; right:100%; width:12rem; height:1px; background:linear-gradient(90deg,transparent,rgba(170,170,170,.7)); }
.news-scrollbar-track { width:100%; height:100%; background:#ababab; position:relative; overflow:hidden; }
.news-scrollbar-thumb { position:absolute; left:0; top:0; height:100%; background:$color-primary; transition:transform .3s,width .3s; }

/* ----- Info 区 Source: ._f00913a8 ----- */
.news-info { position:absolute; left:0; top:9.5rem; width:34.375rem; height:46.75rem; }
.news-info-bg { position:absolute; inset:0; background:rgba(0,0,0,.4); mix-blend-mode:overlay; }
.news-info-inner { height:100%; position:relative; padding-top:2.5rem; padding-left:3.875rem; }

/* ----- 水印 Source: ._ddfc4ee5 ----- */
.news-label { position:absolute; top:100%; left:9rem; white-space:nowrap; overflow:hidden; display:flex; align-items:flex-end; height:.95em; font-family:'Oswald','Arial Black',sans-serif; font-size:7rem; letter-spacing:-0.05em; color:#242424; pointer-events:none; user-select:none; }

/* ----- 主信息 Source: ._e2f809d4 ----- */
.news-main { position:absolute; left:3.875rem; bottom:-1.875rem; width:26.5rem; }
.news-main-date { font-family:monospace; letter-spacing:1px; color:#d2d2d2; font-size:.95rem; }
.news-main-title { font-size:2.25rem; font-weight:700; letter-spacing:2px; color:#fff; margin-top:.25rem; max-height:2.8em; display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:2; overflow:hidden; text-overflow:ellipsis; }
.news-main-url { font-size:.75rem; letter-spacing:2px; margin-top:1rem; color:#606060; }
.news-main-btn { margin-top:2rem; cursor:pointer; width:14.375rem; height:3.75rem; padding:0 1.75rem 0 1rem; white-space:nowrap; display:flex; align-items:center; transition:background-color .3s,color .3s; background:$color-primary; color:#000; text-decoration:none; }
.news-main-btn:hover { background:#fff; color:#000; }
.news-main-btn .btn-main { font-size:1.25rem; }
.news-main-btn .btn-sub { font-size:.875rem; }
.news-main-btn svg { flex:none; width:.5rem; margin-left:auto; }

/* ----- tabs Source: ._8419bfdd ----- */
.news-tabs { display:flex; }
.news-tab { cursor:pointer; display:flex; align-items:center; width:5.625rem; height:1.25em; padding:0 .5rem 0 .125rem; margin-right:1rem; font-weight:700; font-size:.85rem; color:#fff; transition:color .3s,background-color .3s; }
.news-tab:hover { color:$color-primary; }
.news-tab.active { color:#000; background:$color-primary; }
.news-tab svg { flex:none; width:.4375rem; margin-left:auto; transition:opacity .3s; opacity:0; }
.news-tab.active svg { opacity:1; }

/* ----- 文章列表 Source: ._0882dfb6 ----- */
.news-list { margin-top:.5rem; }
.news-item { cursor:pointer; width:22.5rem; height:6rem; border-bottom:1px solid rgba(255,255,255,.3); display:flex; align-items:center; text-decoration:none; }
.news-item:hover .title { color:#fff; }
.news-item .tag { white-space:nowrap; font-weight:700; font-size:1.125rem; color:$color-primary; flex-shrink:0; }
.news-item .info { width:17.5rem; margin-left:auto; color:#d2d2d2; }
.news-item .info .date { white-space:nowrap; font-family:monospace; letter-spacing:1px; font-size:.85rem; }
.news-item .info .title { margin-top:.125rem; font-size:1.125rem; font-weight:700; letter-spacing:2px; max-height:2.8em; display:-webkit-box; -webkit-box-orient:vertical; -webkit-line-clamp:2; overflow:hidden; text-overflow:ellipsis; color:#d2d2d2; }

/* ----- READ MORE Source: ._b9c239f0 ----- */
.news-more-btn { margin-top:2rem; cursor:pointer; width:7.625rem; height:1.5rem; padding:0 .625rem; white-space:nowrap; display:flex; align-items:center; font-size:.875rem; font-weight:700; transition:background-color .3s,color .3s; background:#585858; color:#d2d2d2; text-decoration:none; }
.news-more-btn:hover { background:#fff; color:#000; }
.news-more-btn svg { flex:none; width:.4375rem; margin-left:auto; }

/* ============================================================
   MODE: posts — 现有卡片列表（保留）
   ============================================================ */
.panel-posts { position: absolute; inset: 0; }

.bg-section {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 30vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  background: $bg-dark url(#{$img-post-detail-bg}) center / cover no-repeat;
  background-position-y: 30%;
  z-index: 1;

  .glass-overlay {
    position: absolute; inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    opacity: 0.25;
    pointer-events: none;
  }

  .header-content {
    position: relative; z-index: 2; padding-left: 40px; width: 100%;
    .page-title { font-size: 2.5rem; font-weight: 700; color: $text-primary; margin: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
    .page-subtitle { font-size: 1.1rem; color: $text-primary; margin-top: 8px; }
  }
}

.list-section {
  position: absolute;
  top: 30vh; left: 0; right: 0; bottom: 0;
  display: flex; flex-direction: column;
  overflow: hidden;
  z-index: 2;
  background: $bg-base;
  padding-top: 90px;

  .list-body { flex: 1; overflow-y: auto; padding: 16px 24px 0; }
}

.tab-header {
  flex-shrink: 0;
  display: flex; gap: 20px;
  padding: 20px 24px 0;
  border-bottom: 1px solid rgba(255,255,255,0.08);

  button {
    padding: 10px 8px; background: none; border: none;
    font-size: 0.95rem; color: $text-secondary; cursor: pointer; position: relative;
    transition: color 0.3s;
    &:hover { color: $text-primary; }
    &.active {
      color: $color-primary; font-weight: 600;
      &::after { content: ''; position: absolute; bottom: -5px; left: 0; width: 100%; height: 2.5px; background: $color-primary; }
    }
    &.refresh-btn { margin-left: auto; padding: 10px 12px; font-size: 0.85rem; color: $color-primary; &:disabled { opacity: 0.5; cursor: not-allowed; } }
  }
}

.article-list { display: flex; flex-direction: column; gap: 12px; max-width: 80vw; margin: 0 auto; }

/* ----- 共用状态 ----- */
.state-display {
  padding: 2rem; text-align: center;
  .loading-spinner {
    width: 30px; height: 30px; border: 2px solid rgba(255,255,255,0.08);
    border-top: 2px solid $color-primary; border-radius: 50% !important;
    animation: spin 1s linear infinite; margin: 0 auto 12px;
  }
  .error-msg { color: $color-error; font-size: 1rem; margin-bottom: 1rem; }
  p { font-size: 1rem; color: $text-secondary; }
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
  .news-swiper-wrap {
    top: 5rem; right: 2rem; width: calc(100vw - 4rem); height: 35vh;
  }
  .news-scrollbar-wrap {
    top: calc(5rem + 35vh); width: calc(100vw - 4rem); right: 2rem;
  }
  .news-info {
    left: 2rem; top: calc(5rem + 35vh + 1rem); width: calc(100vw - 4rem); height: auto;
  }
  .news-info-inner { padding: 1.5rem 1.5rem; }
  .news-item { width: 100%; height: auto; padding: .5rem 0; }
  .news-item .info { width: auto; }
  .news-main { position: relative; left: 0; bottom: auto; width: 100%; margin-top: 1.5rem; }
  .news-main-title { font-size: 1.5rem; }

  .bg-section .header-content { padding-left: 20px; .page-title { font-size: 1.8rem; } }
  .list-section .list-body { padding: 12px 16px 0; }
  .article-list { max-width: 90vw; }
}
</style>

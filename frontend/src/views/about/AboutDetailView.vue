<template>
  <div class="about-detail-page">
    <!-- ===== 顶部：文章区域 ===== -->
    <section class="article-section" :class="{ entered: slidIn }">
      <div class="article-container">
        <h1 class="article-title">{{ pageTitle }}</h1>
        <div class="article-content markdown-body" v-html="renderedContent"></div>
      </div>
    </section>

    <!-- ===== 贡献者标题 ===== -->
    <section class="contributors-section" :class="{ entered: slidIn }">
      <div class="contributors-header">
        <h2 class="contributors-title">了解你的贡献者</h2>
        <p class="contributors-subtitle">MEET THE TEAM / 2026</p>
      </div>
    </section>

    <!-- ===== 画廊：5 人矩形 ===== -->
    <section class="gallery-section" :class="{ entered: slidIn }" ref="galleryRef">
      <div
        v-for="(person, idx) in team"
        :key="idx"
        class="gallery-item-wrap"
        :class="{ 'is-hidden': expandedIndex !== -1 && expandedIndex !== idx }"
      >
        <!-- 名字在矩形的上面 -->
        <Transition name="label-fade">
          <div v-if="expandedIndex !== idx" class="person-label">
            <span class="person-name">{{ person.name }}</span>
          </div>
        </Transition>

        <div
          class="gallery-item"
          :class="{ expanded: expandedIndex === idx }"
          :style="getItemStyle(idx)"
          @click="toggleExpand(idx)"
        >
          <div class="person-bg" :style="{ background: person.gradient }"></div>
          <img class="person-img" :src="person.image" :alt="person.name" />

          <!-- 展开时：右侧人物介绍 -->
          <Transition name="detail-slide">
            <div v-if="expandedIndex === idx" class="person-detail">
              <div class="person-info">
                <h2 class="detail-name">{{ person.name }}</h2>
                <p class="detail-role">{{ person.role }}</p>
                <div class="detail-desc markdown-body" v-html="renderMarkdown(person.description)"></div>
                <div v-if="person.quote" class="detail-quote">
                  <span class="quote-label">💬 个人语录</span>
                  <div class="quote-text markdown-body" v-html="renderMarkdown(person.quote)"></div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { renderMarkdown } from '@/utils'

// ===== 状态 =====
const expandedIndex = ref(-1)
const galleryRef = ref(null)
const slidIn = ref(false)

onMounted(() => {
  requestAnimationFrame(() => { slidIn.value = true })
})

// ===== 页面文章 =====
const pageTitle = '关于维特博客'
const pageContent = `
# 维特博客

维特博客是一个专注于技术分享与个人表达的知识平台。

我们相信代码不仅是工具，更是表达思想的方式。通过写作和分享，我们希望帮助更多开发者少走弯路，同时也督促自己不断学习和进步。

## 了解源代码

- ***源代码：https://github.com/xxjyu114514/ViteeBlog***

## 未来的计划

我们正在计划以下功能：

- **更好的样式**：优化 UI 设计，提供更清晰的操作指引
- **优化入场退场动画**
- **前端性能优化**：减轻性能压力，引入限流机制
- **后端重构**：优化石山（提升系统稳健性）

## 一些感慨

做这个其实只是想做一个个人博客交作业而已，奈何想法太多，想到什么加什么。  
我觉得做代码、做网页，还是得做得有意思、有趣、丰富多样，而不是纯应付——虽然最后也没做完 😅

做了 2 个月，和组员交流（撕逼）也收获了很多代码开发的经验，磨练了心性，也磨练了技术，挺好的。虽然说挺累的。

在这里还是要感谢所有这个项目的贡献者们，非常感谢你们！

—— xxjyu

## 特别感谢

- **vue-anime-website** 项目组成员，他们对本项目提供大量技术支持以及灵感启发，了解他们的开源项目！ ***https://github.com/Jackychan-200811/vue-anime-website***
`
const renderedContent = computed(() => renderMarkdown(pageContent))

// ===== 团队成员数据 =====
const team = [
  {
    name: '78区子羽先生',
    role: '创始人 & 全栈工程师',
    description: '擅长 **Vue 3**、**FastAPI**、**MySQL**，专注于构建高性能 Web 应用。热爱开源，持续探索前沿技术。',
    quote: '请支持异世界情绪谢谢 🙏',
    image: new URL('@/assets/team/photo-1.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #0f0c29 0%, #0f0c29 80%, transparent 100%)',
  },
  {
    name: '13区智烨',
    role: 'UI/UX 设计师',
    description: '冷色调设计语言的缔造者。专注毛玻璃与机能风格的融合，追求极致的视觉体验与交互细节。',
    quote: 'Tell Me Tell Me 鏡よ鏡一番 好きな私になるの',
    image: new URL('@/assets/team/photo-2.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #1a1a2e 0%, #1a1a2e 80%, transparent 100%)',
  },
  {
    name: '陈伟权先生',
    role: '后端架构师',
    description: '**Python** 全栈开发者，精通 **FastAPI** 与数据库设计。对 API 性能优化与系统架构有深入理解。',
    quote: '你写不过我你信吗！',
    image: new URL('@/assets/team/photo-3.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #0d1117 0%, #0d1117 80%, transparent 100%)',
  },
  {
    name: '91丘溢聪先生',
    role: '数据库工程师',
    description: '追求 **MySQL** 工程化。追求代码的可维护性和优雅性，致力于打造流畅的用户体验。',
    quote: '劳资头像帅否 🤔',
    image: new URL('@/assets/team/photo-4.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #1b1b2f 0%, #1b1b2f 80%, transparent 100%)',
  },
  {
    name: '周子俊孔龙',
    role: '产品经理 & 内容运营',
    description: '负责博客的内容规划与社区运营。关注开发者成长，致力于打造有温度的技术交流平台。',
    quote: '哈哈哈哈哈哈哈哈哈 😂',
    image: new URL('@/assets/team/photo-5.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #0a0a23 0%, #0a0a23 80%, transparent 100%)',
  },
]

// ===== 展开/折叠 =====
const toggleExpand = (idx) => {
  expandedIndex.value = expandedIndex.value === idx ? -1 : idx
}

// ===== 每项样式 =====
const getItemStyle = (idx) => {
  return {
    height: expandedIndex.value === idx ? 'calc(100vh - 90px)' : '70vh',
  }
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
@use 'sass:color';

.about-detail-page {
  background: $bg-base;
  color: $text-primary;
}

/* ===== 入场动画 ===== */
.article-section,
.contributors-section,
.gallery-section {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.article-section.entered {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0s;
}

.contributors-section.entered {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.15s;
}

.gallery-section.entered {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.3s;
}

/* ===== 顶部文章 ===== */
.article-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 120px 24px 80px;
}

.article-container {
  max-width: 720px;
  width: 100%;
}

.article-title {
  font-family: $font-mono;
  font-size: 3.2rem;
  font-weight: 800;
  color: $text-primary;
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin-bottom: 48px;
}

.article-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: $text-secondary;

  :deep(h2) {
    font-family: $font-mono;
    font-size: 1.4rem;
    font-weight: 700;
    color: $text-primary;
    margin: 32px 0 16px;
    padding-left: 12px;
    border-left: 3px solid $color-primary;
  }

  :deep(p) {
    margin-bottom: 16px;
  }

  :deep(ul) {
    padding-left: 20px;
    li { margin-bottom: 8px; list-style: none; &::before { content: '✦ '; color: $color-primary; } }
  }
}

/* ===== 贡献者标题 ===== */
.contributors-section {
  padding: 80px 24px 40px;
  display: flex;
  justify-content: center;
}

.contributors-header {
  text-align: center;
  max-width: 600px;
}

.contributors-title {
  font-family: $font-mono;
  font-size: 5rem;
  font-weight: 800;
  color: $text-primary;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.contributors-subtitle {
  font-size: 0.85rem;
  color: $text-tertiary;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* ===== 画廊 ===== */
.gallery-section {
  display: flex;
  width: 100vw;
  overflow: hidden;
}

.gallery-item-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: flex 0.6s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.4s ease 0.15s;

  &.is-hidden {
    flex: 0 0 0;
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
    transition: flex 0.5s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.2s ease;
  }
}

.gallery-item {
  position: relative;
  width: 100%;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  transition: height 0.6s cubic-bezier(0.65, 0, 0.35, 1);
}

.person-img {
  position: absolute;
  top: 0;
  left: 0;
  width: auto;
  height: 100%;
  z-index: 1;
  filter: brightness(0.7);
  transition: filter 0.4s;
}

.person-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.gallery-item:hover .person-img {
  filter: brightness(1);
}

/* 折叠时：底部名字 */
.person-label {
  white-space: nowrap;
  letter-spacing: 0.3em;
  margin-bottom: 8px;
}

.person-name {
  font-family: $font-mono;
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
}

/* 展开时：右侧详情 */
.person-detail {
  position: absolute;
  top: 0;
  right: 0;
  width: 40%;
  height: 100%;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to left, rgba(0, 0, 0, 0.7) 0%, transparent 100%);
  padding: 48px;
}

.person-info {
  max-width: 360px;
}

.detail-name {
  font-family: $font-mono;
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}

.detail-role {
  font-family: $font-mono;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.detail-desc {
  font-size: 0.95rem;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.8);
}

.detail-quote {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quote-label {
  font-family: $font-mono;
  font-size: 0.7rem;
  color: $color-primary;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  display: block;
  margin-bottom: 8px;
}

.quote-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.55);
  font-style: italic;
}

/* ===== 名字淡入淡出 ===== */
.label-fade-enter-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.label-fade-leave-active { transition: opacity 0.15s ease; }
.label-fade-enter-from { opacity: 0; transform: translateY(8px); }
.label-fade-leave-to { opacity: 0; }

/* ===== 详情面板滑入 ===== */
.detail-slide-enter-active { transition: opacity 0.4s ease 0.15s, transform 0.4s ease 0.15s; }
.detail-slide-leave-active { transition: opacity 0.2s ease; }
.detail-slide-enter-from { opacity: 0; transform: translateX(40px); }
.detail-slide-leave-to { opacity: 0; }
</style>

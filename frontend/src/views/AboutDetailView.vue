<template>
  <div class="about-detail-page">
    <!-- ===== 顶部：文章区域 ===== -->
    <section class="article-section">
      <div class="article-container">
        <h1 class="article-title">{{ pageTitle }}</h1>
        <div class="article-content markdown-body" v-html="renderedContent"></div>
      </div>
    </section>

    <!-- ===== 画廊：5 人矩形 ===== -->
    <section class="gallery-section" ref="galleryRef">
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
                <p class="detail-desc">{{ person.description }}</p>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { renderMarkdown } from '@/utils'

// ===== 状态 =====
const expandedIndex = ref(-1)
const galleryRef = ref(null)

// ===== 页面文章 =====
const pageTitle = '关于观测笔记'
const pageContent = `
观测笔记 是一个专注于技术分享与个人表达的知识平台。

我们相信代码不仅是工具，更是表达思想的方式。通过写作和分享，我们希望帮助更多开发者少走弯路，同时也督促自己不断学习和进步。

## 我们的理念

- **冷色调机能风** — 设计语言融合明日方舟美学与 GitHub 暗色层次
- **零圆角硬边** — 毛玻璃与硬边结合的独特视觉风格
- **极致性能** — 基于 Vite + Vue 3 构建，追求极致加载体验
`
const renderedContent = computed(() => renderMarkdown(pageContent))

// ===== 团队成员数据 =====
const team = [
  {
    name: 'xxjyu',
    role: '创始人 & 全栈工程师',
    description: '擅长 Vue 3、FastAPI、Mysql 专注于构建高性能 Web 应用。热爱开源，持续探索前沿技术。请支持异世界情绪谢谢',
    image: new URL('@/assets/team/photo-1.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #0f0c29 0%, #0f0c29 80%, transparent 100%)',
  },
  {
    name: '鱼生manman香',
    role: 'UI/UX 设计师',
    description: '冷色调设计语言的缔造者。专注毛玻璃与机能风格的融合，追求极致的视觉体验与交互细节。Tell Me Tell Me 鏡よ鏡一番 好きな私になるの',
    image: new URL('@/assets/team/photo-2.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #1a1a2e 0%, #1a1a2e 80%, transparent 100%)',
  },
  {
    name: '张雪峰先生',
    role: '后端架构师',
    description: 'Python 全栈开发者，精通 FastAPI 与数据库设计。对 API 性能优化与系统架构有深入理解。你写不过我你信吗！',
    image: new URL('@/assets/team/photo-3.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #0d1117 0%, #0d1117 80%, transparent 100%)',
  },
  {
    name: '91丘先生',
    role: '数据库工程师',
    description: '追求mysql工程化。追求代码的可维护性和优雅性，致力于打造流畅的用户体验。劳资头像帅否',
    image: new URL('@/assets/team/photo-4.jpg', import.meta.url).href,
    gradient: 'linear-gradient(to top, #1b1b2f 0%, #1b1b2f 80%, transparent 100%)',
  },
  {
    name: '周孔龙',
    role: '产品经理 & 内容运营',
    description: '负责博客的内容规划与社区运营。关注开发者成长，致力于打造有温度的技术交流平台。哈哈哈哈哈哈哈哈哈',
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
  const base = {
    width: expandedIndex.value === -1 ? '20vw' : expandedIndex.value === idx ? '100vw' : '0',
    height: '70vh',
  }
  return base
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
@use 'sass:color';

.about-detail-page {
  background: $bg-base;
  color: $text-primary;
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

/* ===== 画廊 ===== */
.gallery-section {
  display: flex;
  width: 100vw;
  overflow: hidden;
}

.gallery-item-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: width 0.6s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.4s ease 0.15s;

  &.is-hidden {
    width: 0 !important;
    opacity: 0;
    pointer-events: none;
    transition: width 0.5s cubic-bezier(0.65, 0, 0.35, 1), opacity 0.2s ease;
  }
}

.gallery-item {
  position: relative;
  flex-shrink: 0;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.person-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  object-fit: cover;
  filter: brightness(0.7);
  transition: filter 0.4s, width 0.6s cubic-bezier(0.65, 0, 0.35, 1);
}

.person-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

/* 展开时：图片缩到左边40%，渐变背景自然露出来 */
.gallery-item.expanded .person-img {
  width: 40%;
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

<template>
  <div class="about-container">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <section class="about-hero">
      <h1 class="glass-text">About Me</h1>
    </section>

    <div 
      class="about-main" 
      :style="{ marginTop: mainMarginTop }"
    >
      <!-- 个人简介卡片 -->
      <div class="content-card bio-section">
        <div class="avatar-section">
          <div class="avatar-placeholder">
            {{ getInitials() }}
          </div>
          <div class="user-info">
            <h2>观测笔记作者</h2>
            <p class="role">全栈开发者 & 技术博主</p>
            <div class="social-links">
              <a href="#" class="social-link">GitHub</a>
              <a href="#" class="social-link">Twitter</a>
              <a href="#" class="social-link">Email</a>
            </div>
          </div>
        </div>
        
        <div class="bio-content">
          <h3>关于这个博客</h3>
          <p>这是一个记录技术成长、分享开发经验的个人博客。在这里，我会分享Vue 3、Python、FastAPI等技术栈的实战经验，以及对前端工程化、性能优化等方面的思考。</p>
          
          <h3>我的理念</h3>
          <p>代码不仅是工具，更是表达思想的方式。通过写作和分享，我希望帮助更多开发者少走弯路，同时也督促自己不断学习和进步。</p>
        </div>
      </div>
      
      <!-- 技术栈展示 -->
      <div class="content-card tech-section">
        <h2>技术栈</h2>
        <div class="tech-grid">
          <div class="tech-item">
            <h4>前端</h4>
            <div class="tech-tags">
              <span class="tech-tag">Vue 3</span>
              <span class="tech-tag">Vite</span>
              <span class="tech-tag">TypeScript</span>
              <span class="tech-tag">Pinia</span>
              <span class="tech-tag">SCSS</span>
            </div>
          </div>
          <div class="tech-item">
            <h4>后端</h4>
            <div class="tech-tags">
              <span class="tech-tag">Python</span>
              <span class="tech-tag">FastAPI</span>
              <span class="tech-tag">SQLAlchemy</span>
              <span class="tech-tag">PostgreSQL</span>
            </div>
          </div>
          <div class="tech-item">
            <h4>DevOps</h4>
            <div class="tech-tags">
              <span class="tech-tag">Docker</span>
              <span class="tech-tag">Git</span>
              <span class="tech-tag">CI/CD</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 经历时间线 -->
      <div class="content-card timeline-section">
        <h2>经历时间线</h2>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <h4>2026 - 现在</h4>
              <p>专注于Vue 3 + Vite技术栈，开发现代化博客系统</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <h4>2025 - 2026</h4>
              <p>深入研究Python后端开发，掌握FastAPI框架</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <h4>2024 - 2025</h4>
              <p>开始前端开发之旅，学习Vue.js生态系统</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

// 滚动偏移状态
const scrollY = ref(0)

const handleScroll = () => {
  scrollY.value = window.scrollY
}

// 计算动态的margin-top值，实现平滑过渡
const mainMarginTop = computed(() => {
  // 基础偏移 -100px，随着滚动增加覆盖量，最大到 -150px
  const baseOffset = -100
  const scrollOffset = Math.min(scrollY.value * 0.3, 50) // 滚动影响系数0.3，最大额外偏移50px
  return `${baseOffset - scrollOffset}px`
})

const handleBack = () => {
  if (isAnimating.value) return
  router.push('/about-immersive')
}

const getInitials = () => {
  return 'OB'
}

// 监听滚动事件
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>

</style>

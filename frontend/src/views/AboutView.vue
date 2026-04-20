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
.back-button {
  position: fixed;
  top: 100px;
  left: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
  }
}

.about-container {
  width: 100%;
  background: #f0f2f5;
  min-height: 100vh;
}

.about-hero {
  height: 50vh;
  background: #1a1a1a url('@/assets/about-bg.webp') center/cover;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  position: relative;
  /* 固定背景，创建视差效果 */
  background-attachment: fixed;
}

.about-main {
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  margin-top: -100px; /* 默认偏移，会被动态样式覆盖 */
  padding: 0 20px 100px;
  position: relative;
  z-index: 2;
  background: #f0f2f5;
  /* 添加圆角和阴影，增强覆盖效果 */
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.1);
  transition: margin-top 0.1s ease-out;
}

.content-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.bio-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

@media (min-width: 768px) {
  .bio-section {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .avatar-section {
    display: flex;
    gap: 20px;
    align-items: center;
  }
  
  .avatar-placeholder {
    width: 80px;
    height: 80px;
    font-size: 2rem;
  }
  
  .user-info {
    text-align: left;
  }
  
  .bio-content {
    margin-top: 0;
  }
}

.role {
  color: #6b7280;
  margin: 8px 0;
}

.social-links {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.social-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.9rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tech-tag {
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #4b5563;
}

.timeline {
  margin-top: 20px;
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 25px;
}

.timeline-dot {
  position: absolute;
  left: -28px;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  border: 3px solid white;
}

.timeline-content h4 {
  margin: 0 0 8px 0;
  color: #1f2937;
}

.timeline-content p {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}
</style>

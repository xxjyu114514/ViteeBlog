<template>
  <div 
    class="about-immersive-wrapper page-wrapper-base" 
    @wheel="handleWheel"
    @click="handleClick"
  >
    <section class="hero-static flex-center">
      <div class="hero-content">
        <div class="icon-box">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 14C7.5 14 4 16.5 4 19V20H20V19C20 16.5 16.5 14 12 14Z" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </div>
        <h1 class="glass-text">关于我</h1>
        <p class="intro-text">ABOUT ME / 2026</p>
        <div class="enter-hint">
          <span>点击进入详情</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('about-immersive')

const handleClick = () => {
  router.push('/about')
}
</script>

<style lang="scss" scoped>
.about-immersive-wrapper {
  overflow: hidden;
  background: #111;
  cursor: pointer;
}

.hero-static {
  width: 100%; 
  height: 100%;
  background: #111 url('../assets/hero-bg.jpg') center/cover no-repeat;
  color: white;
}

.hero-content {
  text-align: center; 
  z-index: 10;
  
  .icon-box {
    margin-bottom: 20px;
    svg {
      width: 80px; 
      height: 80px; 
      color: white;
      opacity: 0.8;
    }
  }
  
  .glass-text {
    font-size: 3.5rem; 
    font-weight: 700; 
    letter-spacing: 4px;
    background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.5) 100%);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;
  }
  
  .intro-text {
    font-size: 1.1rem; 
    color: rgba(255, 255, 255, 0.7);
    text-transform: uppercase; 
    letter-spacing: 2px;
  }
  
  .enter-hint {
    margin-top: 40px;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.9rem;
    animation: pulse 2s infinite;
    
    @keyframes pulse {
      0%, 100% { opacity: 0.5; }
      50% { opacity: 1; }
    }
  }
}
</style>
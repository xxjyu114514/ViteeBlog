<template>
  <div 
    class="message-immersive-wrapper page-wrapper-base" 
    @wheel="handleWheel"
    @click="handleClick"
  >
    <section class="hero-static flex-center">
      <div class="hero-content">
        <div class="icon-box">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15C21 16.1046 20.1046 17 19 17H7L3 21V5C3 3.89543 3.89543 3 5 3H19C20.1046 3 21 3.89543 21 5V15Z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 10H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M15 10H15.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M9 10H9.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h1 class="glass-text">留言板</h1>
        <p class="intro-text">MESSAGE BOARD / 2026</p>
        <div class="enter-hint">
          <span>点击进入留言</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('message-immersive')

const handleClick = () => {
  router.push('/message')
}
</script>

<style lang="scss" scoped>
.message-immersive-wrapper {
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
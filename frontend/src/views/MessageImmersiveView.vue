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
        
        <!-- 增加留言统计 -->
        <div class="stats-preview">
          <span class="stat-item">📝 128条留言</span>
          <span class="stat-item">💬 45位访客</span>
        </div>
        
        <!-- 增加最新留言预览 -->
        <div class="latest-message">
          <p class="message-author">来自 @技术爱好者：</p>
          <p class="message-content">博客内容很实用，期待更多分享！</p>
        </div>
        
        <div class="enter-hint">
          <span>点击进入留言互动</span>
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

</style>
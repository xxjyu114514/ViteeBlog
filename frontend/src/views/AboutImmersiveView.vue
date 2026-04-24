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
        
        <!-- 增加个人标签预览 -->
        <div class="tags-preview">
          <span class="tag">Vue 3</span>
          <span class="tag">Python</span>
          <span class="tag">观测笔记</span>
          <span class="tag">技术分享</span>
        </div>
        
        <!-- 增加简短个人介绍 -->
        <p class="bio-preview">记录技术成长与生活感悟的观测者</p>
        
        <div class="enter-hint">
          <span>点击查看完整介绍</span>
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

</style>
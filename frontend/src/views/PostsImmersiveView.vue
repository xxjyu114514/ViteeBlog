<template>
  <div 
    class="posts-immersive-wrapper page-wrapper-base" 
    @wheel="handleWheel"
    @click="handleClick"
  >
    <section class="hero-static flex-center">
      <div class="hero-content">
        <div class="icon-box">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.19907 4.73223 2.73223C5.20107 2.2654 5.83696 2 6.5 2Z" stroke="currentColor" stroke-width="1.5"/>
            <path d="M4 10H12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M4 14H8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <h1 class="glass-text">文章列表</h1>
        <p class="intro-text">ARTICLES / 2026</p>
        <div class="enter-hint">
          <span>点击进入文章详情</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('posts-immersive')

const handleClick = () => {
  router.push('/posts')
}
</script>

<style lang="scss" scoped>

</style>
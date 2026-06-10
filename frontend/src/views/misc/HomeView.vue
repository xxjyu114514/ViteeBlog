<template>
  <div class="home-view-wrapper page-wrapper-base" @wheel="handleWheel">
    <!-- 始终显示沉浸式封面，不受登录状态影响 -->
    <section class="hero-static">
      <div class="hero-content">
        <h1 class="glass-text">维特博客</h1>
        <p class="intro-text">ViteeBlog / 2026</p>
        <p class="site-desc">记录技术思考，分享知识沉淀。<br>用文字连接每一个热爱编码的灵魂。</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

// 维持项目原有的滚轮导航逻辑
const { handleWheel } = usePrimaryPageWheel('home')
</script>
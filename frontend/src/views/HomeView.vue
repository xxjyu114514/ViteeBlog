<template>
  <div class="home-view-wrapper page-wrapper-base" @wheel="handleWheel">
    <!-- 始终显示沉浸式封面，不受登录状态影响 -->
    <section class="hero-static">
      <div class="hero-content">
        <h1 class="glass-text">观测笔记</h1>
        <p class="intro-text">Observational Notes / 2026</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

// 维持项目原有的滚轮导航逻辑
const { handleWheel } = usePrimaryPageWheel('home')
</script>

<style lang="scss" scoped>

</style>
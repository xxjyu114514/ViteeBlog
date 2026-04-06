<template>
  <Navbar />
  
  <router-view v-slot="{ Component, route }">
    <transition @enter="onEnter" @leave="onLeave" :css="false">
      <component 
        :is="Component" 
        :key="route.path" 
        :class="['page-wrapper', { 'padding-page': !isImmersivePage }]" 
      />
    </transition>
  </router-view>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { usePageTransition } from './composables/usePageTransition'

const route = useRoute()
const { onEnter, onLeave } = usePageTransition()

// 定义哪些页面需要“首页样式”（沉浸式、无占位）
const isImmersivePage = computed(() => {
  const immersivePaths = ['/', '/login']
  return immersivePaths.includes(route.path)
})
</script>

<style lang="scss">
.page-wrapper {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 1;
  overflow-y: auto;
  background: white; // 默认底色
}

// 非沉浸页面（如文章列表、关于等）自动顶开导航栏高度
.padding-page {
  padding-top: 90px; 
}
</style>
<template>
  <Navbar />
  
  <router-view v-slot="{ Component, route }">
    <transition @enter="onEnter" @leave="onLeave" :css="false">
      <component 
        :is="Component" 
        :key="route.path" 
        :class="['page-wrapper-base', { 'padding-page': !isImmersivePage }]" 
      />
    </transition>
  </router-view>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { usePageTransition } from './composables/usePageTransition'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const { onEnter, onLeave } = usePageTransition()

// 判断是否为沉浸式页面（无顶部导航栏）
const isImmersivePage = computed(() => {
  const immersiveRoutes = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']
  return immersiveRoutes.includes(route.name)
})

// 添加页面可见性检查
const userStore = useUserStore()
let visibilityCheckTimer = null

const checkTokenOnVisibilityChange = () => {
  if (!document.hidden) {
    // 页面变为可见时检查token
    if (userStore.checkTokenExpiry()) {
      console.log('页面可见时检测到token过期，已登出')
    }
  }
}

const setupVisibilityCheck = () => {
  // 页面可见性变化时检查
  document.addEventListener('visibilitychange', checkTokenOnVisibilityChange)
  
  // 定时检查（作为补充，每5分钟）
  visibilityCheckTimer = setInterval(() => {
    if (!document.hidden && userStore.isAuthenticated) {
      userStore.checkTokenExpiry()
    }
  }, 300000) // 5分钟
}

const cleanupVisibilityCheck = () => {
  document.removeEventListener('visibilitychange', checkTokenOnVisibilityChange)
  if (visibilityCheckTimer) {
    clearInterval(visibilityCheckTimer)
    visibilityCheckTimer = null
  }
}

onMounted(() => {
  setupVisibilityCheck()
})

onUnmounted(() => {
  cleanupVisibilityCheck()
})
</script>

<style scoped>
/* ... existing styles ... */
</style>
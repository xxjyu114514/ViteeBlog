<template>
  <nav :class="['navbar-fixed', { 'is-immersive': isImmersiveMode }]">
    <div v-if="isImmersiveMode" class="dynamic-blur-layer"></div>
    
    <div class="nav-container container flex-between">
      <div class="logo-section">
        <span class="logo-text">OBSERVATION</span>
      </div>
      
      <div class="menu-links">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path" 
          :to="item.path" 
          class="nav-item"
        >
          {{ item.name }}
        </router-link>
      </div>

      <div class="nav-right">
        <!-- 未登录状态：显示LOGIN按钮 -->
        <router-link 
          v-if="!userStore.isAuthenticated" 
          to="/login" 
          class="login-btn"
        >
          LOGIN
        </router-link>
        
        <!-- 已登录状态：显示个人主页入口 -->
        <router-link 
          v-else 
          to="/personal" 
          class="personal-btn"
        >
          个人中心
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const menuItems = [
  { name: '首页', path: '/' },
  { name: '文章', path: '/posts-immersive' },
  { name: '关于', path: '/about-immersive' },
  { name: '留言', path: '/message-immersive' }
]

// 统一判定沉浸模式
const isImmersiveMode = computed(() => {
  return ['/', '/posts-immersive', '/about-immersive', '/message-immersive', '/login', '/personal'].includes(route.path)
})

import "./navbar.scss"
</script>

<style lang="scss" scoped>

</style>
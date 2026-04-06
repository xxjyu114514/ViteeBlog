<template>
  <nav :class="['navbar-fixed', { 'is-immersive': isImmersiveMode }]">
    
    <div v-if="isImmersiveMode" class="glass-gradient-bg"></div>
    
    <div class="nav-container">
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
        <router-link to="/login" class="login-btn">LOGIN</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const menuItems = [
  { name: '首页', path: '/' },
  { name: '文章', path: '/posts' },
  { name: '关于', path: '/about' },
  { name: '留言', path: '/message' }
]

// 核心：首页和登录页都触发沉浸式样式
const isImmersiveMode = computed(() => {
  return ['/', '/login'].includes(route.path)
})
</script>

<style lang="scss" scoped>
.navbar-fixed {
  position: fixed;
  top: 0; left: 0;
  width: 100%;
  height: 90px;
  z-index: 9999;
  display: flex;
  align-items: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  // --- 【常规页面模式】（默认） ---
  background: #ffffff;
  color: #000000;
  border-bottom: 2px solid #000000; 

  // --- 【沉浸模式：首页 & 登录页】 ---
  &.is-immersive {
    color: #ffffff;
    border-bottom: none !important; 
    
    // 沉浸式的渐变遮罩背景
    background: linear-gradient(
      to bottom, 
      rgba(0, 0, 0, 0.8) 0%, 
      rgba(0, 0, 0, 0.4) 60%,
      rgba(0, 0, 0, 0) 100%
    ) !important;
  }
}

.glass-gradient-bg {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 120px; 
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  pointer-events: none;
  z-index: -1;
  
  mask-image: linear-gradient(to bottom, black 0%, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 0%, black 60%, transparent 100%);
}

// ... 剩下的 nav-container, nav-item 样式保持你原来的即可 ...
.nav-container {
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section .logo-text {
  font-weight: 900;
  letter-spacing: 3px;
  font-size: 1.25rem;
}

.menu-links {
  display: flex;
  gap: 50px;
  
  .nav-item {
    text-decoration: none;
    color: inherit;
    font-size: 1rem;
    font-weight: 800;
    position: relative;
    padding: 10px 0;
    
    background: none !important;
    border: none !important;

    &:hover { opacity: 0.7; }
    
    &.router-link-active {
      &::after {
        content: '';
        position: absolute;
        bottom: -5px; 
        left: 50%;
        transform: translateX(-50%);
        width: 6px; height: 6px;
        background: currentColor;
        border-radius: 50%;
      }
    }
  }
}

.login-btn {
  text-decoration: none;
  color: inherit;
  font-weight: 800;
  font-size: 0.85rem;
  letter-spacing: 2px;
  border: none !important;
}
</style>
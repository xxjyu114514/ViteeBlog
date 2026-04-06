<template>
  <nav :class="[
    'navbar', 
    { 
      'is-dark-style': isDarkStyle, 
      'animating': isAnimating 
    }
  ]">
    <div class="nav-container">
      <div class="logo-section">
        <span class="logo-text">观测笔记</span>
        <span class="logo-dot">.</span>
      </div>
      
      <div class="menu-links">
        <router-link to="/" class="nav-item">首页</router-link>
        <router-link to="/posts" class="nav-item">文章</router-link>
        <router-link to="/about" class="nav-item">关于</router-link>
        <router-link to="/message" class="nav-item">留言板</router-link>
      </div>

      <div class="nav-right">
        <router-link 
          to="/login" 
          :class="['login-link-btn', { 'is-hidden': isLoginPage }]"
        >
          登录
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePageTransition } from '@/composables/usePageTransition'

const route = useRoute()
const { isAnimating } = usePageTransition()

// 判断逻辑：仅在首页和登录页使用“深色背景”适配样式（白色文字+高级毛玻璃）
const isHomePage = computed(() => route.name === 'home')
const isLoginPage = computed(() => route.name === 'login')
const isDarkStyle = computed(() => isHomePage.value || isLoginPage.value)
</script>

<style lang="scss" scoped>
.navbar {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 70px;
  z-index: 10000;
  display: flex;
  align-items: center;
  transition: all 0.5s cubic-bezier(0.645, 0.045, 0.355, 1);
  
  // 默认：白天模式（白底黑字）
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: #1d1d1f;

  // 核心：统一的液体玻璃质感（首页和登录页共享）
  &.is-dark-style {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(15px) saturate(160%) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
  }

  &.animating {
    pointer-events: none;
    opacity: 0.6;
  }
}

.nav-container {
  width: 100%; max-width: 1200px;
  margin: 0 auto; padding: 0 40px;
  display: flex; justify-content: space-between; align-items: center;
}

.logo-section {
  font-size: 1.25rem; font-weight: 700;
  .logo-dot { color: #3b82f6; }
}

.menu-links {
  display: flex; gap: 8px;
  .nav-item {
    text-decoration: none; color: inherit;
    padding: 8px 18px; border-radius: 12px;
    transition: all 0.3s ease;
    position: relative;
    
    &:hover { background: rgba(120, 120, 120, 0.1); }
    &.router-link-active::after {
      content: ''; position: absolute; bottom: 4px; left: 50%;
      transform: translateX(-50%); width: 4px; height: 4px;
      border-radius: 50%; background: currentColor;
    }
  }
}

.nav-right .login-link-btn {
  text-decoration: none; padding: 8px 22px; border-radius: 20px;
  font-size: 0.9rem; font-weight: 600;
  background: #1d1d1f; color: #fff;
  transition: all 0.4s ease;

  .is-dark-style & {
    background: #ffffff; color: #1d1d1f;
    &:hover { background: #3b82f6; color: #fff; }
  }

  &.is-hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
  }
}
</style>
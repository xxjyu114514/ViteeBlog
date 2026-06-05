<template>
  <nav class="navbar-fixed is-immersive">
    <div class="dynamic-blur-layer"></div>
    
    <div class="nav-container container flex-between">
      <div class="logo-section">
        <Transition name="logo-swap" mode="out-in">
          <span v-if="!showBackBtn" key="logo" class="logo-text">OBSERVATION</span>
          <button v-else key="back" class="btn-back" @click="router.back()"><</button>
        </Transition>
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
        <!-- 搜索入口 -->
        <router-link to="/search" class="search-icon" title="搜索文章">🔍</router-link>
        
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
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 不需要返回按钮的顶层页面
const mainPages = ['/', '/posts-immersive', '/about-immersive', '/message-immersive', '/personal']
const showBackBtn = computed(() => !mainPages.includes(route.path))

const menuItems = [
  { name: '首页', path: '/' },
  { name: '文章', path: '/posts-immersive' },
  { name: '关于', path: '/about-immersive' },
  { name: '留言', path: '/message-immersive' }
]
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

/* ===== 导航栏容器：透明底，让毛玻璃层显现 ===== */
.navbar-fixed {
  position: fixed;
  top: 0; left: 0;
  width: 100%;
  height: 90px;
  z-index: 9999;
  display: flex;
  align-items: center;
  background: transparent;
  border-bottom: none;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
  background: #333;
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  padding: 6px 16px;
  border: none;
  border-radius: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  &:active { filter: brightness(0.7); }
}

/* ===== 毛玻璃层（保留原创设计） ===== */
.dynamic-blur-layer {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 140px;
  pointer-events: none;
  z-index: -1;
  backdrop-filter: blur(30px) saturate(180%) brightness(0.85);
  -webkit-backdrop-filter: blur(30px) saturate(180%) brightness(0.85);
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0) 100%
  );
  mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 100%);
}

.nav-container {
  padding: 0 50px;
  width: 100%;
}

.logo-text {
  font-weight: 900;
  letter-spacing: 3px;
  font-size: 1.25rem;
  color: $text-primary;
}

.menu-links {
  display: flex;
  gap: 50px;
}

.nav-item {
  text-decoration: none;
  font-size: 1rem;
  font-weight: 800;
  position: relative;
  padding: 10px 0;
  transition: opacity 0.3s;
  color: $text-primary;
}

.nav-item:hover {
  opacity: 0.7;
}

.nav-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -5px; 
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: $text-primary;
  border-radius: 50%;
}

.search-icon {
  text-decoration: none;
  font-size: 1.1rem;
  margin-right: 16px;
  opacity: 0.7;
  transition: opacity 0.2s;
  &:hover { opacity: 1; }
}

.login-btn,
.personal-btn {
  text-decoration: none;
  font-weight: 800;
  font-size: 0.85rem;
  letter-spacing: 2px;
  color: $text-primary;
}

/* ===== 标题 ↔ 返回按钮切换动画 ===== */
.logo-swap-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.logo-swap-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.logo-swap-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}
.logo-swap-leave-to {
  opacity: 0;
  transform: translateX(12px);
}
</style>

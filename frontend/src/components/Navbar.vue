<template>
  <nav class="navbar-fixed is-immersive" :class="{ 'navV2': useNavV2 }">
    <div class="dynamic-blur-layer"></div>
    
    <div class="nav-container container flex-between">
      <div class="logo-section">
        <Transition name="logo-swap" mode="out-in">
          <span v-if="!showBackBtn" key="logo" class="logo-text">ViteeBlog</span>
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
import { useNavV2 } from '@/composables/useStyleSwitch'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 不需要返回按钮的顶层页面
const mainPages = ['/', '/posts-immersive', '/about-immersive', '/message-immersive', '/personal']
const showBackBtn = computed(() => !mainPages.includes(route.path))

const menuItems = [
  { name: '首页', path: '/' },
  { name: '文章', path: '/posts-immersive' },
  { name: '留言', path: '/message-immersive' },
  { name: '关于', path: '/about-immersive' }
]
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

/* ============================================================
   基础：老样式（原始 px / rem，无 --ui-scale）
   ============================================================ */
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

.dynamic-blur-layer {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 140px;
  pointer-events: none;
  z-index: -1;
  backdrop-filter: blur(30px) saturate(180%) brightness(0.85);
  -webkit-backdrop-filter: blur(30px) saturate(180%) brightness(0.85);
  background: linear-gradient(to bottom, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
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
  color: #f0f4fa;
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
  color: #f0f4fa;
}

.nav-item:hover { opacity: 0.7; }

.nav-item.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -5px; left: 50%;
  transform: translateX(-50%);
  width: 6px; height: 6px;
  background: #f0f4fa;
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

.login-btn, .personal-btn {
  text-decoration: none;
  font-weight: 800;
  font-size: 0.85rem;
  letter-spacing: 2px;
  color: #f0f4fa;
}

/* ===== 标题 ↔ 返回按钮切换动画 ===== */
.logo-swap-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.logo-swap-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.logo-swap-enter-from { opacity: 0; transform: translateX(-12px); }
.logo-swap-leave-to   { opacity: 0; transform: translateX(12px); }

/* ============================================================
   .navV2：新样式覆盖（--ui-scale 缩放 + 字体特殊化）
   改 useNavV2 ref 即可切换
   ============================================================ */
.navV2.navbar-fixed       { height: calc(5.625rem * var(--ui-scale)); }
.navV2 .dynamic-blur-layer { height: calc(8.75rem * var(--ui-scale)); }
.navV2 .nav-container      { padding: 0 calc(3.125rem * var(--ui-scale)); }
.navV2 .menu-links         { gap: calc(3.125rem * var(--ui-scale)); }
.navV2 .logo-text          { letter-spacing: calc(0.1875rem * var(--ui-scale)); font-size: calc(1.25rem * var(--ui-scale)); color: #f0f4fa; }
.navV2 .btn-back           { min-width: calc(6.25rem * var(--ui-scale)); font-size: calc(1.1rem * var(--ui-scale)); padding: calc(0.375rem * var(--ui-scale)) calc(1rem * var(--ui-scale)); }
.navV2 .search-icon        { font-size: calc(1.1rem * var(--ui-scale)); margin-right: calc(1rem * var(--ui-scale)); }
.navV2 .login-btn,
.navV2 .personal-btn       { font-size: calc(0.85rem * var(--ui-scale)); letter-spacing: calc(0.125rem * var(--ui-scale)); color: #f0f4fa; }

.navV2 .nav-item {
  font-size: calc(2rem * var(--ui-scale));
  font-weight: 900;
  font-family: 'Oswald', 'Arial Black', 'Impact', sans-serif;
  letter-spacing: calc(0.25rem * var(--ui-scale));
  text-transform: uppercase;
  padding: calc(0.625rem * var(--ui-scale)) 0;
  color: #f0f4fa;
}

.navV2 .nav-item.router-link-active::after {
  bottom: calc(-0.3125rem * var(--ui-scale));
  width: calc(0.375rem * var(--ui-scale));
  height: calc(0.375rem * var(--ui-scale));
}

.navV2 .logo-swap-enter-from { transform: translateX(calc(-0.75rem * var(--ui-scale))); }
.navV2 .logo-swap-leave-to   { transform: translateX(calc(0.75rem * var(--ui-scale))); }
</style>

<template>
  <nav :class="['navbar-fixed', { 'is-immersive': isImmersiveMode }]">
    <div v-if="isImmersiveMode" class="dynamic-blur-layer"></div>
    
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

// 统一判定沉浸模式
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
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);

  // --- 默认：常规页面（白底黑线） ---
  background: #ffffff;
  color: #000000;
  border-bottom: 1px solid #000000;

  // --- 沉浸模式：首页 & 登录页 ---
  &.is-immersive {
    background: transparent; // 必须透明，否则看不到背景
    color: #ffffff;
    border-bottom: none !important;
  }
}

.dynamic-blur-layer {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 140px; // 比导航栏稍深，产生向下扩散的空气感
  pointer-events: none;
  z-index: -1;

  // 【核心黑科技】：
  // 1. blur(30px): 提供磨砂玻璃质感
  // 2. saturate(180%): 这是关键！它会强行抓取背景图的色彩并放大
  // 3. brightness(0.85): 略微压低亮度，确保白色文字在浅色背景图上依然清晰
  backdrop-filter: blur(30px) saturate(180%) brightness(0.85);
  -webkit-backdrop-filter: blur(30px) saturate(180%) brightness(0.85);

  // 【物理遮罩】：给一个极淡的主体色层，增加色彩厚度
  // 这里用 rgba(255,255,255, 0.03) 增加通透性，或者 rgba(0,0,0,0.1) 增加稳重感

  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0) 100%
  );

  // 【边缘消融】：让毛玻璃效果不是生硬切断，而是随渐变消失
  mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 100%);
}

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
    font-weight: 800; // 纯字粗体
    position: relative;
    padding: 10px 0;
    transition: opacity 0.3s;
    
    &:hover { opacity: 0.7; }
    
    // 选中小点
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
}
</style>
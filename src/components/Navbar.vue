<template>
  <nav 
    :class="['navbar-fixed', { 'is-immersive': isImmersiveMode }]"
    :style="navStyle"
  >
    <div v-if="isImmersiveMode" class="glass-gradient-bg"></div>
    
    <div class="nav-container">
      <div class="logo-section">
        <span class="logo-text">OBSERVATION</span>
      </div>
      
      <div class="menu-links">
        <router-link v-for="item in menuItems" :key="item.path" :to="item.path" class="nav-item">
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

// 模拟动态主题色逻辑
const navStyle = computed(() => {
  if (route.path === '/') return { '--nav-mask-color': '10, 12, 16' } // 首页：深冷色调
  if (route.path === '/login') return { '--nav-mask-color': '20, 15, 30' } // 登录：暗紫色调
  return {}
})

const isImmersiveMode = computed(() => ['/', '/login'].includes(route.path))
const menuItems = [
  { name: '首页', path: '/' },
  { name: '文章', path: '/posts' },
  { name: '关于', path: '/about' },
  { name: '留言', path: '/message' }
]
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
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);

  // 默认：白底黑字
  background: #ffffff;
  color: #000000;
  border-bottom: 2px solid #000000;

  &.is-immersive {
    color: #ffffff;
    border-bottom: none !important;
    
    // 【关键】使用变量控制渐变色。rgb内填入变量，让遮罩带上色彩倾向
    // 这里用了 0.85 到 0 的过度，保证顶部文字清晰
    background: linear-gradient(
      to bottom,
      rgba(var(--nav-mask-color, 0, 0, 0), 0.85) 0%,
      rgba(var(--nav-mask-color, 0, 0, 0), 0.4) 50%,
      rgba(var(--nav-mask-color, 0, 0, 0), 0) 100%
    ) !important;
  }
}

.glass-gradient-bg {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 140px; // 稍微加深范围
  // 【关键】毛玻璃不仅模糊，还通过滤镜强化背景的主题色感
  backdrop-filter: blur(25px) saturate(150%) brightness(0.9);
  -webkit-backdrop-filter: blur(25px) saturate(150%) brightness(0.9);
  pointer-events: none;
  z-index: -1;
  
  // 渐变蒙版，让毛玻璃边缘消失得极其柔和
  mask-image: linear-gradient(to bottom, black 0%, black 40%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 0%, black 40%, transparent 100%);
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
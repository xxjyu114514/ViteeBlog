<template>
  <div 
    class="post-page-wrapper" 
    ref="scrollContainer"
    @wheel="handleWheel"
  >
    <div class="nav-placeholder"></div>

    <div class="content-scroller">
      <PostList />
    </div>
    
    <div :class="['top-indicator', { 'ready': touchTopState === 1 }]">
      <span>继续上划返回首页</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import PostList from '@/components/PostList.vue'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

// 获取容器引用以监控容器内滚动高度
const scrollContainer = ref(null)
const touchTopState = ref(0)
let resetTimer = null

const handleWheel = (e) => {
  if (isAnimating.value) return

  // 【核心修复】：判定容器自身的 scrollTop
  const isAtTop = scrollContainer.value ? scrollContainer.value.scrollTop <= 5 : true
  const isScrollingUp = e.deltaY < 0

  if (isAtTop && isScrollingUp) {
    if (touchTopState.value === 0) {
      touchTopState.value = 1
      clearTimeout(resetTimer)
      resetTimer = setTimeout(() => { 
        touchTopState.value = 0 
      }, 1500)
    } else if (touchTopState.value === 1) {
      router.push('/')
      touchTopState.value = 0
    }
  } else {
    touchTopState.value = 0
  }
}

onUnmounted(() => { 
  clearTimeout(resetTimer) 
})
</script>

<style lang="scss" scoped>
.post-page-wrapper {
  width: 100%;
  height: 100vh; 
  overflow-y: auto; // 滚动条在这里
  background: #ffffff;
  scroll-behavior: smooth;
  position: relative;
}

// 站位块高度同步 Navbar (90px)
.nav-placeholder {
  width: 100%;
  height: 90px;
  background: transparent;
}

.content-scroller {
  max-width: 1100px;
  margin: 0 auto;
}

.top-indicator {
  position: fixed; 
  top: 110px; // 避开导航栏
  left: 50%; 
  transform: translateX(-50%);
  padding: 10px 24px; 
  background: rgba(0,0,0,0.8); 
  backdrop-filter: blur(10px);
  color: white;
  border-radius: 30px; 
  font-size: 0.9rem; 
  opacity: 0; 
  pointer-events: none;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  z-index: 9999;

  &.ready { 
    opacity: 1; 
    transform: translateX(-50%) translateY(10px); 
  }
}
</style>
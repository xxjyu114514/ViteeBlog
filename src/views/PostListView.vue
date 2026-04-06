<template>
  <div class="post-page-wrapper" @wheel="handleWheel">
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
const touchTopState = ref(0)
let resetTimer = null

const handleWheel = (e) => {
  if (isAnimating.value) return
  const isAtTop = window.scrollY <= 0
  const isScrollingUp = e.deltaY < 0

  if (isAtTop && isScrollingUp) {
    if (touchTopState.value === 0) {
      touchTopState.value = 1
      clearTimeout(resetTimer)
      resetTimer = setTimeout(() => { touchTopState.value = 0 }, 1500)
    } else if (touchTopState.value === 1) {
      router.push('/')
      touchTopState.value = 0
    }
  } else {
    touchTopState.value = 0
  }
}

onUnmounted(() => { clearTimeout(resetTimer) })
</script>

<style lang="scss" scoped>
.post-page-wrapper {
  width: 100%; min-height: 100vh; background: #fbfbfd;
}
.top-indicator {
  position: fixed; top: 80px; left: 50%; transform: translateX(-50%);
  padding: 8px 20px; background: rgba(0,0,0,0.6); color: white;
  border-radius: 20px; font-size: 0.85rem; opacity: 0; transition: 0.3s;
  &.ready { opacity: 1; transform: translateX(-50%) translateY(10px); }
}
</style>
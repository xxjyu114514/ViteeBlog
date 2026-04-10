<template>
  <div class="post-page-wrapper page-wrapper-base">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="content-scroller container">
      <PostList />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import PostList from '@/components/PostList.vue'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

const handleBack = () => {
  if (isAnimating.value) return
  router.push('/posts-immersive')
}
</script>

<style lang="scss" scoped>
.post-page-wrapper {
  overflow-y: auto; // 滚动条在这里
  background: var(--bg-white);
  scroll-behavior: smooth;
  position: relative;
}

.content-scroller {
  max-width: 1100px;
  margin: 0 auto;
}

.back-button {
  position: fixed;
  top: 100px;
  left: 20px;
  z-index: 1000;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
  }
}
</style>
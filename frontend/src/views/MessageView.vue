<template>
  <div class="page-container">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <h1>留言板</h1>
    <p>访客可以在这里留言，博主会进行回复 [cite: 17]。</p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

const handleBack = () => {
  if (isAnimating.value) return
  router.push('/message-immersive')
}
</script>

<style scoped>
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

.page-container {
  padding: 100px 20px;
  text-align: center;
}
</style>
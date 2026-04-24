<template>
  <div class="post-page-wrapper page-wrapper-base">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="content-scroller container">
      <PostList ref="postListRef" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PostList from '@/components/PostList.vue'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()
const postListRef = ref(null)

const handleBack = () => {
  if (isAnimating.value) return
  router.push('/posts-immersive')
}

// 确保每次进入页面都刷新文章列表
onMounted(() => {
  // 延迟一点时间确保组件已挂载
  setTimeout(() => {
    if (postListRef.value && postListRef.value.refresh) {
      postListRef.value.refresh()
    }
  }, 100)
})
</script>

<style lang="scss" scoped>

</style>
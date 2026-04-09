<template>
  <div class="home-view-wrapper page-wrapper-base" @wheel="handleWheel">
    <section class="hero-static flex-center">
      <div class="hero-content">
        <div class="avatar-box">
          <img src="../assets/avatar.png" class="avatar" alt="头像" />
        </div>
        <h1 class="glass-text">观测笔记</h1>
        <p class="intro-text">Observational Notes / 2026</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePageTransition } from '@/composables/usePageTransition'

const router = useRouter()
const { isAnimating } = usePageTransition()

const handleWheel = (e) => {
  if (isAnimating.value) return
  if (e.deltaY > 0) {
    router.push('/posts')
  }
}
</script>

<style lang="scss" scoped>
.home-view-wrapper {
  overflow: hidden;
  background: #111;
}

.hero-static {
  width: 100%; height: 100%;
  background: #111 url('../assets/hero-bg.jpg') center/cover no-repeat;
  color: white;
}

.hero-content {
  text-align: center; z-index: 10;
  .avatar-box {
    margin-bottom: 20px;
    .avatar {
      width: 120px; height: 120px; border-radius: 50%;
      border: 2px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(5px);
    }
  }
  .glass-text {
    font-size: 3.5rem; font-weight: 700; letter-spacing: 4px;
    background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.5) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .intro-text {
    font-size: 1.1rem; color: rgba(255, 255, 255, 0.7);
    text-transform: uppercase; letter-spacing: 2px;
  }
}
</style>
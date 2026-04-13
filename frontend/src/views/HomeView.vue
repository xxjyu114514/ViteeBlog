<template>
  <div class="home-view-wrapper page-wrapper-base" @wheel="handleWheel">
    <!-- 未登录状态：显示沉浸式封面 -->
    <section v-if="!userStore.isAuthenticated" class="hero-static">
      <div class="hero-content">
        <h1 class="glass-text">观测笔记</h1>
        <p class="intro-text">Observational Notes / 2026</p>
      </div>
    </section>
    
    <!-- 已登录状态：显示个人中心 -->
    <PersonalCenterView v-else />
  </div>
</template>

<script setup>
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'
import { useUserStore } from '@/stores/user'
import PersonalCenterView from './PersonalCenterView.vue'

// 获取用户状态
const userStore = useUserStore()

// 维持项目原有的滚轮导航逻辑，但只在未登录时启用
const { handleWheel } = usePrimaryPageWheel('home')
</script>

<style lang="scss" scoped>
.home-view-wrapper {
  overflow: hidden;
  background: #111; // 沉浸式页面的深色背景
}

.hero-static {
  position: relative; // 必须为 relative 才能让 content 绝对定位到左下角
  width: 100%; 
  height: 100%;
  // 引用项目资源目录下的背景图
  background: #111 url('../assets/hero-bg.jpg') center/cover no-repeat;
  color: white;
}

.hero-content {
  position: absolute;
  left: 60px;   // 距离左边距离
  bottom: 80px; // 距离底部距离，模仿锁屏界面样式
  text-align: left;
  z-index: 10;
  
  /* 应用您注册的 PingFang SC Heavy 字体 */
  font-family: 'PingFangHeavy', "PingFang SC", sans-serif;

  .glass-text {
    /* 1. 基础样式：改小、极粗、苹方 Heavy */
    font-size: 2.4rem; 
    font-weight: 900; 
    letter-spacing: -0.5px;
    margin: 0;
    line-height: 1.1;

    /* 2. 实现半透明玻璃感的核心 */
    /* 使用高透明度的白色渐变，模拟玻璃的反射感 */
    background: linear-gradient(
      160deg, 
      rgba(255, 255, 255, 0.8) 0%, 
      rgba(255, 255, 255, 0.5) 50%,
      rgba(255, 255, 255, 0.3) 100%
    );
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;

    /* 3. 增强质感：通过 filter 模拟毛玻璃的厚度感 */
    /* drop-shadow 提供文字阴影，blur 模拟边缘的柔和折射感 */
    filter: drop-shadow(0 4px 15px rgba(0, 0, 0, 0.3)) blur(0.4px);
    
    /* 4. 可选：由于文字无法直接 backdrop-filter，我们给容器加一个极淡的模糊底色层 */
    position: relative;
    &::before {
      content: '观测笔记';
      position: absolute;
      left: 0; top: 0;
      z-index: -1;
      color: transparent;
      /* 这里的模糊会透出背景颜色，产生一种文字区域都在发光的效果 */
      text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }
  }

  .intro-text {
    font-size: 0.9rem;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 8px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }

  position: absolute;
    left: 60px;
    bottom: 80px;
    padding: 20px 30px;
    
}

/* 适配移动端，防止文字溢出屏幕 */
@media (max-width: 768px) {
  .hero-content {
    left: 30px;
    bottom: 50px;
    .glass-text { font-size: 1.8rem; }
  }
}
</style>
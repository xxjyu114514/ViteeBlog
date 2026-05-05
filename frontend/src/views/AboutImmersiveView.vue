<template>
  <div 
    class="about-immersive-wrapper" 
    @wheel="handleWheel"
  >
    <!-- 背景底层 -->
    <div class="base-hero-image"></div>

    <div class="immersive-overlay">
      
      <!-- 左侧面板 -->
      <transition name="slice-left" appear>
        <div class="side-panel left-panel">
          <div class="content-box">
            <h1 class="title">关于我们</h1>
            <p class="desc">致力于打造沉浸式的数字交互体验。</p>
          </div>
        </div>
      </transition>

      <!-- 中间空隙 -->
      <div class="center-gap"></div>

      <!-- 右侧面板：点击事件现在绑定在整个容器上 -->
      <transition name="slice-right" appear>
        <div 
          class="side-panel right-panel" 
          @click="navToAboutDetail"
        >
          <div class="action-box">
            <p class="hint">点击了解更多</p>
            <span class="arrow">→</span>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('about-immersive')

const navToAboutDetail = () => {
  router.push('/about')
}
</script>

<style lang="scss" scoped>
$skew-width: 12vw;

.about-immersive-wrapper {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  background: #000;
  z-index: 10;
}

.base-hero-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('../assets/hero-bg.webp') center center / cover no-repeat;
  z-index: 1;
}

.immersive-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  z-index: 2;
  display: flex;
}

.side-panel {
  height: 100%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  will-change: transform;
}

/* 左侧面板样式维持原样 */
.left-panel {
  flex: 1.5;
  clip-path: polygon(0 0, 100% 0, calc(100% - #{$skew-width}) 100%, 0 100%);
  padding-right: 5vw;

  .content-box {
    text-align: center;
    .title {
      font-family: 'PingFang SC Heavy', sans-serif;
      font-size: clamp(2rem, 5vw, 3.5rem);
      margin: 0;
    }
    .desc {
      color: #666;
      font-size: 1rem;
      margin-top: 1.5vh;
    }
  }
}

.center-gap {
  width: 18vw;
  background: transparent;
}

/* 右侧面板：现在它是整个可点击的按钮 */
.right-panel {
  flex: 1;
  clip-path: polygon(#{$skew-width} 0, 100% 0, 100% 100%, 0 100%);
  padding-left: 5vw;
  cursor: pointer; /* 整个区域鼠标悬停显示手型 */
  transition: background-color 0.3s ease; /* 可选：添加背景色微变效果 */

  // 悬停时让整个白色区域稍微亮一点或暗一点，给用户反馈
  &:hover {
    background-color: #f9f9f9;
    
    .arrow {
      transform: translateX(10px); /* 悬停时箭头动效 */
    }
  }

  .action-box {
    text-align: center;
    pointer-events: none; /* 防止内部元素干扰点击事件的冒泡 */
    
    .hint {
      font-family: 'PingFang SC Heavy', sans-serif;
      font-size: clamp(1rem, 1.5vw, 1.2rem);
      margin-bottom: 0.5rem;
    }
    .arrow {
      font-size: 2rem;
      display: inline-block;
      transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    }
  }
}

/* 动画部分保持不变 */
.slice-left-enter-active, .slice-right-enter-active {
  transition: transform 1.2s cubic-bezier(0.22, 1, 0.36, 1), opacity 1.2s ease;
}
.slice-left-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}
.slice-right-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

:global(body) {
  margin: 0;
  overflow: hidden !important;
}
</style>
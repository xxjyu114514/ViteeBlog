<template>
  <div class="about-immersive-wrapper" @wheel.prevent="handleCustomWheel">
    <div class="base-hero-image"></div>

    <div class="immersive-overlay">
      <div class="side-panel left-panel">
        <div class="content-box">
          <h1 class="title">关于我们</h1>
          <p class="desc">致力于打造沉浸式的数字交互体验。</p>
        </div>
      </div>

      <div class="center-gap">
        <div 
          class="shutter-active-layer" 
          :class="{ 'is-moved': isMoved }"
        ></div>

        <div 
          class="shutter-exit-layer" 
          :class="{ 'is-closing': isExiting }"
        ></div>
      </div>

      <div class="side-panel right-panel" @click="navToAboutDetail">
        <div class="action-box">
          <p class="hint">点击了解更多</p>
          <span class="arrow">→</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePrimaryPageWheel } from '@/composables/usePrimaryPageWheel'

const router = useRouter()
const { handleWheel } = usePrimaryPageWheel('about-immersive')

const isMoved = ref(false)
const isExiting = ref(false)

onMounted(() => {
  const isBackNavigation = window.history.state?.back === '/message-immersive' || router.lastDir === 'up' 

  if (isBackNavigation) {
    // 【切入场景 A】从后页滚回来
    isMoved.value = true
    isExiting.value = true 
    
    // 初始对齐卡点：260ms 边缘精准对齐中线
    setTimeout(() => {
      isExiting.value = false 
    }, 260) 
  } else {
    // 【切入场景 B】从首页初次进入
    isMoved.value = false
    setTimeout(() => {
      isMoved.value = true 
    }, 260)
  }
})

const handleCustomWheel = (e) => {
  if (e.deltaY > 0) {
    /* --- 向下滚动：去往下一页（切出） --- */
    if (!isMoved.value) {
      isMoved.value = true
    } else if (!isExiting.value) {
      // 1. 启动快门平行四边形下落遮挡
      isExiting.value = true
      
      // 📐 向下切出：0ms 零延迟出发。
      // 滚动动画过半时（约 260ms），平行四边形【底边】正好向下斩过屏幕正中（50vh）。
      handleWheel(e) 
    }
  } else if (e.deltaY < 0) {
    /* --- 向上滚动：原路返回（回滚切入） --- */
    // 1. 状态同时复位，平行四边形开始向上抽离退场
    isExiting.value = false 
    isMoved.value = false 
    
    // ⚡ 核心修改：向上回滚零延迟触发 handleWheel(e)，与向下滚动形成完美的镜像对称
    // 滚轮往上一路晃，抽离动画和上一页路由滚动动画【在同一起跑线 0ms 同时启动】。
    // 在动画进行到 260ms 时，路由滚动动画到达最中间。
    // 此时往上收缩的平行四边形【顶边】也刚好以最高速抬到屏幕正中间（50vh），两条边缘效果正好相反且完全对称！
    handleWheel(e)
  }
}

const navToAboutDetail = () => {
  router.push('/about-detail')
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

$skew-width: 12vw; 
$gap-width: 18vw;

/* ==========================================================================
   📐 双向边缘（下落看底边 / 抽离看顶边）中线绝对对称调速面板
   ========================================================================== */
$anim-duration-enter: 0.8s;  /* 进场总时间统一为 0.8s */
$anim-duration-exit:  0.8s;  /* 离场总时间统一为 0.8s */

/* 工业级高精度非线性 EaseOut 曲线，确保在 260ms 处不论上下都能完成 50% 的几何位移 */
$anim-curve: cubic-bezier(0.25, 1, 0.5, 1); 

.shutter-active-layer {
  transition: transform #{$anim-duration-enter} #{$anim-curve};
}

.shutter-exit-layer {
  transition: transform #{$anim-duration-exit} #{$anim-curve};
}

/* ==========================================================================
   快门图层基础样式
   ========================================================================== */
.shutter-active-layer, .shutter-exit-layer {
  position: absolute;
  top: 0;
  left: -20vw;
  width: calc(#{$gap-width} + 40vw);
  height: 100%;
  background: $bg-surface;
  z-index: 5;
  clip-path: polygon(#{$skew-width} 0, 100% 0, calc(100% - #{$skew-width}) 100%, 0 100%);
  will-change: transform;
  pointer-events: none;
}

/* 动画 A：向左下撤离（显露内容） */
.shutter-active-layer {
  transform: translate(0, 0); 
  &.is-moved {
    transform: translate(-#{$skew-width}, 100vh); 
  }
}

/* 动画 B：离场/滚回（向下时底边往下切入视口；回滚时顶边往上收回掠过中线） */
.shutter-exit-layer {
  transform: translate(#{$skew-width}, -100vh); 
  &.is-closing {
    transform: translate(0, 0); 
  }
}

/* 基础自适应布局 */
.about-immersive-wrapper { width: 100vw; height: 100vh; position: fixed; top: 0; left: 0; overflow: hidden; background: $bg-base; z-index: 10; }
.base-hero-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: url(#{$img-about-bg}) center center / cover no-repeat; z-index: 1; }
.immersive-overlay { position: relative; width: 100%; height: 100%; z-index: 4; display: flex; }
.side-panel { height: 100%; background: $bg-surface; display: flex; align-items: center; justify-content: center; }
.left-panel { flex: 1.5; clip-path: polygon(0 0, 100% 0, calc(100% - #{$skew-width}) 100%, 0 100%); padding-right: 5vw; }
.center-gap { width: $gap-width; position: relative; }
.right-panel { flex: 1; clip-path: polygon(#{$skew-width} 0, 100% 0, 100% 100%, 0 100%); padding-left: 5vw; cursor: pointer; }
.title { font-family: 'PingFang SC Heavy'; font-size: 4rem; margin: 0; color: $text-primary; }
.desc { color: $text-secondary; margin-top: 1rem; font-size: 1.2rem; }
.arrow { font-size: 2rem; display: inline-block; margin-top: 10px; color: $text-secondary; }
</style>
<template>
  <Navbar />

  <!-- 装饰线系统（1:1 复制 Arknights ._60828c90） -->
  <div class="deco-lines show" :class="'deco-panel-' + decoPanel">
    <div class="deco-dot deco-vline"></div>
    <div class="deco-dot deco-hline-top"></div>
    <div class="deco-dot deco-hline-bot"></div>
  </div>

  <router-view v-slot="{ Component, route }">
    <transition @enter="onTransitionEnter" @leave="onTransitionLeave" :css="false">
      <component 
        :is="Component" 
        :key="componentKey" 
        :class="['page-wrapper-base', { 'padding-page': !isImmersivePage, 'card-page': route.meta?.noCardTransition }]" 
      />
    </transition>
  </router-view>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { usePageTransition } from './composables/usePageTransition'

const route = useRoute()
const router = useRouter()
const { onEnter, onLeave } = usePageTransition()

// 判断是否为沉浸式页面
const isImmersivePage = computed(() => {
  const immersiveRoutes = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']
  return immersiveRoutes.includes(route.name)
})

// 稳定 key
const componentKey = computed(() => {
  if (route.name === 'posts-immersive' || route.name === 'posts') return 'post-page'
  if (route.name === 'message-immersive' || route.name === 'message') return 'message-page'
  return route.path
})

// 装饰线面板索引（对标 Arknights deco-panel-{0,1}）
const decoPanel = computed(() => {
  return route.name === 'posts-immersive' ? 1 : 0
})

// 包装过渡动画
const hasCardTransition = (r) => r?.meta?.noCardTransition

const onTransitionEnter = (el, done) => {
  if (hasCardTransition(route)) { done(); return }
  onEnter(el, done)
}

const onTransitionLeave = (el, done) => {
  if (hasCardTransition(route)) { done(); return }
  onLeave(el, done)
}
</script>

<style scoped>
/* ============================================================
   装饰线系统（1:1 复制 Arknights style.css 第 93-126 行）
   3条 1px 半透明白线，随路由切换坐标
   ============================================================ */

/* 容器：固定全屏，pointer-events 穿透 */
.deco-lines {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9998;
  pointer-events: none;
  overflow: hidden;
  opacity: 0;
  transition: opacity 0.4s;
}
.deco-lines.show { opacity: 1; }

/* 基类：1px 点，带背景色、transition */
.deco-dot {
  position: absolute;
  z-index: 1;
  background: rgba(255, 255, 255, .3);
  width: 1px;
  height: 1px;
  transition: transform 1s, left 1s, right 1s, top 1s, bottom 1s;
}

/* 竖线：覆盖 height: 100% */
.deco-vline {
  right: 14.75rem;
  top: 0;
  height: 100%;
  width: 1px;
}
.deco-vline::after {
  content: '';
  display: block;
  width: 1px;
  height: 100%;
  background: inherit;
}

/* 横线上：覆盖 width: 100% */
.deco-hline-top {
  top: 0;
  left: 0;
  width: 100%;
  height: 1px;
}

/* 横线下：覆盖 width: 100% */
.deco-hline-bot {
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
}

/* panel 0：默认 — 三线在画面边缘 */
.deco-panel-0 .deco-vline { right: 14.75rem; }
.deco-panel-0 .deco-hline-top { top: 0; }
.deco-panel-0 .deco-hline-bot { bottom: 0; }

/* panel 1：文章沉浸页 — 顶横线滑入 9.5rem（对标 Arknights deco-panel-1） */
.deco-panel-1 .deco-vline { right: 14.75rem; }
.deco-panel-1 .deco-hline-top { top: 9.5rem; }
.deco-panel-1 .deco-hline-bot { bottom: -.25rem; }
</style>

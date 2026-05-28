  <template>
  <Navbar />
  
  <router-view v-slot="{ Component, route }">
    <transition @enter="onTransitionEnter" @leave="onTransitionLeave" :css="false">
      <component 
        :is="Component" 
        :key="route.path" 
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

// 包装过渡动画：如果目标/来源路由有 noCardTransition，跳过动画
const hasCardTransition = (r) => r?.meta?.noCardTransition

const onTransitionEnter = (el, done) => {
  if (hasCardTransition(route) || hasCardTransition(router.currentRoute.value)) {
    done(); return
  }
  onEnter(el, done)
}

const onTransitionLeave = (el, done) => {
  if (hasCardTransition(route) || hasCardTransition(router.currentRoute.value)) {
    done(); return
  }
  onLeave(el, done)
}
</script>

<style scoped>
/* ... existing styles ... */
</style>

<!-- 全局：卡片页面（noCardTransition）父容器强制全屏 -->
<style>
.page-wrapper-base.card-page {
  width: 100vw !important;
  min-width: 100vw !important;
  background: url(./assets/personl.png) right top / cover fixed, #0a0a0c !important;
}
</style>
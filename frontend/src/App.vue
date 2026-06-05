  <template>
  <Navbar />
  
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

// 稳定 key：/posts-immersive 和 /posts 使用相同 key 以复用同一组件实例
const componentKey = computed(() => {
  if (route.name === 'posts-immersive' || route.name === 'posts') return 'post-page'
  return route.path
})

// 包装过渡动画：如果路由有 noCardTransition，跳过动画（仅给后台管理等非过渡页面使用）
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

<!-- 卡片页面背景由 index.scss 提供 -->

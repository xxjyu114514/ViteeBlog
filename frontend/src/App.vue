  <template>
  <Navbar />
  
  <router-view v-slot="{ Component, route }">
    <transition @enter="onEnter" @leave="onLeave" :css="false">
      <component 
        :is="Component" 
        :key="route.path" 
        :class="['page-wrapper-base', { 'padding-page': !isImmersivePage }]" 
      />
    </transition>
  </router-view>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { usePageTransition } from './composables/usePageTransition'

const route = useRoute()
const { onEnter, onLeave } = usePageTransition()

// 判断是否为沉浸式页面（无顶部导航栏）
const isImmersivePage = computed(() => {
  const immersiveRoutes = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']
  return immersiveRoutes.includes(route.name)
})
</script>

<style scoped>
/* ... existing styles ... */
</style>
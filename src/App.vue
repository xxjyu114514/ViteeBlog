<template>
  <Navbar />
  <router-view v-slot="{ Component, route }">
    <transition @enter="onEnter" @leave="onLeave" :css="false">
      <component :is="Component" :key="route.path" class="page-wrapper" />
    </transition>
  </router-view>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import { usePageTransition } from './composables/usePageTransition'
const { onEnter, onLeave } = usePageTransition()
</script>

<style lang="scss">
.page-wrapper {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: white;
  overflow-y: auto;
}
</style>
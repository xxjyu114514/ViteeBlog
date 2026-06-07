import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

import coreRoutes from './modules/core'
import articleRoutes from './modules/article'
import authRoutes from './modules/auth'
import userRoutes from './modules/user'
import adminRoutes from './modules/admin'
import commentRoutes from './modules/comment'
import aboutRoutes from './modules/about'
import messageRoutes from './modules/message'
import miscRoutes from './modules/misc'

const routes = [
  ...coreRoutes,
  ...articleRoutes,
  ...authRoutes,
  ...userRoutes,
  ...adminRoutes,
  ...commentRoutes,
  ...aboutRoutes,
  ...messageRoutes,
  ...miscRoutes,
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guestOnly && userStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    alert('权限不足：此功能仅限管理员使用')
    next('/personal')
  } else {
    next()
  }
})

router.afterEach((to) => {
  const baseTitle = '观测笔记'
  document.title = to.meta.title ? `${to.meta.title} - ${baseTitle}` : baseTitle
})

export default router

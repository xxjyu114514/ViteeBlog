import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 1. 静态导入核心页面
import HomeView from '../views/HomeView.vue'
import PostListView from '../views/PostListView.vue'
import PostsImmersiveView from '../views/PostsImmersiveView.vue'
import AboutImmersiveView from '../views/AboutImmersiveView.vue'
import MessageImmersiveView from '../views/MessageImmersiveView.vue'

// 2. 懒加载功能页面
const AboutView = () => import('../views/AboutView.vue')
const MessageView = () => import('../views/MessageView.vue')
const LoginView = () => import('../views/LoginView.vue')
const PersonalCenterView = () => import('../views/PersonalCenterView.vue')
const ArticleDetailView = () => import('../views/ArticleDetailView.vue')

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { index: 0, title: '首页' }
  },
  {
    path: '/posts-immersive',
    name: 'posts-immersive',
    component: PostsImmersiveView,
    meta: { index: 1, title: '文章列表' }
  },
  {
    path: '/posts',
    name: 'posts',
    component: PostListView,
    meta: { index: 10, title: '文章列表' }
  },
  {
    path: '/article/:id',
    name: 'article-detail',
    component: ArticleDetailView,
    meta: { index: 11, title: '文章详情' }
  },
  {
    path: '/about-immersive',
    name: 'about-immersive',
    component: AboutImmersiveView,
    meta: { index: 2, title: '关于我' }
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { index: 20, title: '关于我' }
  },
  {
    path: '/message-immersive',
    name: 'message-immersive',
    component: MessageImmersiveView,
    meta: { index: 3, title: '留言板' }
  },
  {
    path: '/message',
    name: 'message',
    component: MessageView,
    meta: { index: 30, title: '留言板' }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { index: 4, title: '账号登录', guestOnly: true }
  },
  {
    path: '/personal',
    name: 'personal',
    component: PersonalCenterView,
    meta: { index: 5, title: '个人中心', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

// 核心：路由守卫
router.beforeEach((to, from, next) => {
  // 必须在守卫函数内部获取 store，否则会触发 getActivePinia() 报错
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    // 未登录尝试进入需要权限的页面 -> 强制跳转登录
    next('/login')
  } else if (to.meta.guestOnly && userStore.isAuthenticated) {
    // 已登录尝试进入“仅限游客”页面（如登录页） -> 强制重定向回首页
    next('/')
  } else {
    next()
  }
})

// 动态修改标题
router.afterEach((to) => {
  const baseTitle = '观测笔记'
  document.title = to.meta.title ? `${to.meta.title} - ${baseTitle}` : baseTitle
})

export default router
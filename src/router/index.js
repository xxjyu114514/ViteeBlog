import { createRouter, createWebHistory } from 'vue-router'

// 1. 静态导入核心页面
import HomeView from '../views/HomeView.vue'
import PostListView from '../views/PostListView.vue'

// 2. 懒加载其他功能页面（提高加载性能）
const AboutView = () => import('../views/AboutView.vue')
const MessageView = () => import('../views/MessageView.vue')
const LoginView = () => import('../views/LoginView.vue') // 导入你刚写的登录页

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { index: 0, title: '首页' } // [cite: 5]
  },
  {
    path: '/posts',
    name: 'posts',
    component: PostListView,
    meta: { index: 1, title: '文章列表' } // [cite: 8]
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { index: 2, title: '关于我' } // [cite: 16]
  },
  {
    path: '/message',
    name: 'message',
    component: MessageView,
    meta: { index: 3, title: '留言板' } // [cite: 17]
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    // 将 index 设为 4，这样从任何导航页跳到登录页都会是“前进”动画
    // 如果你希望登录页独立，也可以根据需要调整
    meta: { index: 4, title: '账号登录' } // [cite: 19]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 切换页面时自动回到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局后置守卫：动态修改网页标题 
router.afterEach((to) => {
  const baseTitle = '观测笔记'
  document.title = to.meta.title ? `${to.meta.title} - ${baseTitle}` : baseTitle
})

export default router
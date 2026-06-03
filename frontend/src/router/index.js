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
const ArticleManageView = () => import('../views/ArticleManageView.vue')
const ArticleEditView = () => import('../views/ArticleEditView.vue')
const TestScssView = () => import('../views/test_scss.vue')

const routes = [
  {
    path: '/test-scss',
    name: 'test-scss',
    component: TestScssView,
    meta: { index: 99, title: 'SCSS 测试页面' }
  },
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
    path: '/manage-articles',
    component: ArticleManageView,
    meta: { requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/categories',
    component: () => import('@/views/CategoryManageView.vue'),
    meta: { requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/tags',
    component: () => import('@/views/TagManageView.vue'),
    meta: { requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/comment-reports',
    component: () => import('@/views/CommentReportListView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/comment-admin',
    component: () => import('@/views/CommentAdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/article-import',
    component: () => import('@/views/ArticleImportView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/admin-dashboard',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/users/:id',
    name: 'user-profile',
    component: () => import('@/views/UserProfileView.vue'),
    meta: { index: 15, title: '用户主页', noCardTransition: true }
  },
  {
    path: '/edit-article',
    name: 'article-edit',
    component: ArticleEditView,
    meta: { index: 7, title: '编辑文章', requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/edit-article/:id',
    name: 'article-edit-detail',
    component: ArticleEditView,
    meta: { index: 8, title: '编辑文章', requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('@/views/FavoritesView.vue'),
    meta: { index: 12, title: '我的收藏', requiresAuth: true, noCardTransition: true }
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
    path: '/archive',
    name: 'archive',
    component: () => import('@/views/ArchiveView.vue'),
    meta: { index: 14, title: '文章归档' }
  },
  {
    path: '/message',
    name: 'message',
    component: MessageView,
    meta: { index: 30, title: '留言板' }
  },
  {
    path: '/social',
    name: 'social',
    component: () => import('@/views/SocialView.vue'),
    meta: { index: 13, title: '社交关系', requiresAuth: true, noCardTransition: true }
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

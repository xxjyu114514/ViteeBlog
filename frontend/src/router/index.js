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
const DesignSystemView = () => import('../views/_design.vue')
const SearchView = () => import('../views/SearchView.vue')
const ArchiveView = () => import('../views/ArchiveView.vue')
const AdminImportView = () => import('../views/AdminImportView.vue')
const UserProfileView = () => import('../views/UserProfileView.vue')

const routes = [
  {
    path: '/design-system',
    name: 'design-system',
    component: DesignSystemView,
    meta: { index: 99, title: '设计系统展示' }
  },
  {
    path: '/test_scss',
    name: 'test_scss',
    component: () => import('../views/test_scss.vue'),  // 使用懒加载
    meta: { index: 100, title: 'SCSS组件测试', hidden: true }  // hidden 可选的，表示不在导航中显示
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
    meta: { requiresAuth: true }
  },
  {
    path: '/tags',
    component: () => import('@/views/TagManageView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/comment-reports',
    component: () => import('@/views/CommentReportListView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/comment-admin',
    component: () => import('@/views/CommentAdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
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
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
    meta: { index: 40, title: '搜索文章' }
  },
  {
    path: '/archive',
    name: 'archive',
    component: ArchiveView,
    meta: { index: 41, title: '文章归档' }
  },
  {
    path: '/admin-import',
    name: 'admin-import',
    component: AdminImportView,
    meta: { index: 42, title: '导入管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/user/:id',
    name: 'user-profile',
    component: UserProfileView,
    meta: { index: 43, title: '用户主页' }
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

import HomeView from '@/views/misc/HomeView.vue'
import PostPage from '@/views/article/PostPage.vue'
import AboutImmersiveView from '@/views/about/AboutImmersiveView.vue'
import MessageImmersiveView from '@/views/message/MessageImmersiveView.vue'

export default [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { index: 0, title: '首页' }
  },
  {
    path: '/posts-immersive',
    name: 'posts-immersive',
    component: PostPage,
    meta: { index: 1, title: '文章列表' }
  },
  {
    path: '/posts',
    name: 'posts',
    component: PostPage,
    meta: { index: 10, title: '文章列表' }
  },
  {
    path: '/about-immersive',
    name: 'about-immersive',
    component: AboutImmersiveView,
    meta: { index: 2, title: '关于我' }
  },
  {
    path: '/message-immersive',
    name: 'message-immersive',
    component: MessageImmersiveView,
    meta: { index: 3, title: '留言板' }
  },
]

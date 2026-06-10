import HomeView from '@/views/misc/HomeView.vue'
import PostPageRouter from '@/views/article/PostPageRouter.vue'
import AboutImmersiveView from '@/views/about/AboutImmersiveView.vue'
import MessagePage from '@/views/message/MessagePage.vue'

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
    component: PostPageRouter,
    meta: { index: 1, title: '文章列表' }
  },
  {
    path: '/posts',
    name: 'posts',
    component: PostPageRouter,
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
    component: MessagePage,
    meta: { index: 3, title: '留言板' }
  },
]

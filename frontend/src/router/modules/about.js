const AboutView = () => import('@/views/about/AboutView.vue')
const AboutDetailView = () => import('@/views/about/AboutDetailView.vue')

export default [
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { index: 20, title: '关于我' }
  },
  {
    path: '/about-detail',
    name: 'about-detail',
    component: AboutDetailView,
    meta: { index: 21, title: '关于观测笔记' }
  },
]

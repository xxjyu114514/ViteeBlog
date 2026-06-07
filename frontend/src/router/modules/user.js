const PersonalCenterView = () => import('@/views/user/PersonalCenterView.vue')
const UserProfileView = () => import('@/views/user/UserProfileView.vue')
const SocialView = () => import('@/views/user/SocialView.vue')
const FavoritesView = () => import('@/views/user/FavoritesView.vue')

export default [
  {
    path: '/personal',
    name: 'personal',
    component: PersonalCenterView,
    meta: { index: 5, title: '个人中心', requiresAuth: true }
  },
  {
    path: '/users/:id',
    name: 'user-profile',
    component: UserProfileView,
    meta: { index: 15, title: '用户主页', noCardTransition: true }
  },
  {
    path: '/social',
    name: 'social',
    component: SocialView,
    meta: { index: 13, title: '社交关系', requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: FavoritesView,
    meta: { index: 12, title: '我的收藏', requiresAuth: true, noCardTransition: true }
  },
]

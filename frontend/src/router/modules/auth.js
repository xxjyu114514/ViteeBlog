const LoginView = () => import('@/views/auth/LoginView.vue')

export default [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { index: 4, title: '账号登录', guestOnly: true }
  },
]

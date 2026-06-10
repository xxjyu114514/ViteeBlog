const MessagePage = () => import('@/views/message/MessagePage.vue')

export default [
  {
    path: '/message',
    name: 'message',
    component: MessagePage,
    meta: { index: 30, title: '留言板' }
  },
]

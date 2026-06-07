const MessageView = () => import('@/views/message/MessageView.vue')

export default [
  {
    path: '/message',
    name: 'message',
    component: MessageView,
    meta: { index: 30, title: '留言板' }
  },
]

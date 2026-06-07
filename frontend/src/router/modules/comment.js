const CommentAdminView = () => import('@/views/comment/CommentAdminView.vue')
const CommentReportListView = () => import('@/views/comment/CommentReportListView.vue')

export default [
  {
    path: '/comment-reports',
    component: CommentReportListView,
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/comment-admin',
    component: CommentAdminView,
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
]

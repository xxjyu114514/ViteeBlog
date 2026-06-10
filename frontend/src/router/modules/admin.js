const AdminDashboardView = () => import('@/views/admin/AdminDashboardView.vue')
const AdminImportView = () => import('@/views/admin/AdminImportView.vue')
const CategoryManageView = () => import('@/views/admin/CategoryManageView.vue')
const TagManageView = () => import('@/views/admin/TagManageView.vue')
const UserManageView = () => import('@/views/admin/UserManageView.vue')

export default [
  {
    path: '/admin-dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/admin-users',
    name: 'admin-users',
    component: UserManageView,
    meta: { index: 43, title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin-import',
    name: 'admin-import',
    component: AdminImportView,
    meta: { index: 42, title: '导入管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/categories',
    component: CategoryManageView,
    meta: { requiresAuth: true, noCardTransition: true }
  },
  {
    path: '/tags',
    component: TagManageView,
    meta: { requiresAuth: true, noCardTransition: true }
  },
]

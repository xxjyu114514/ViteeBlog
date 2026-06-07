const ArticleDetailView = () => import('@/views/article/ArticleDetailView.vue')
const ArticleManageView = () => import('@/views/article/ArticleManageView.vue')
const ArticleEditView = () => import('@/views/article/ArticleEditView.vue')
const ArticleImportView = () => import('@/views/article/ArticleImportView.vue')
const ArchiveView = () => import('@/views/article/ArchiveView.vue')
const SearchView = () => import('@/views/article/SearchView.vue')
const PostListView = () => import('@/views/article/PostListView.vue')

export default [
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
    path: '/article-import',
    component: ArticleImportView,
    meta: { requiresAuth: true, requiresAdmin: true, noCardTransition: true }
  },
  {
    path: '/archive',
    name: 'archive',
    component: ArchiveView,
    meta: { index: 14, title: '文章归档' }
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
    meta: { index: 40, title: '搜索文章' }
  },
  {
    path: '/posts-list',
    name: 'posts-list',
    component: PostListView,
    meta: { index: 41, title: '文章列表' }
  },
]

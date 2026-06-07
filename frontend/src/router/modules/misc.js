const DesignSystemView = () => import('@/views/misc/_design.vue')
const TestScssView = () => import('@/views/misc/test_scss.vue')

export default [
  {
    path: '/design-system',
    name: 'design-system',
    component: DesignSystemView,
    meta: { index: 99, title: '设计系统展示' }
  },
  {
    path: '/test_scss',
    name: 'test_scss',
    component: TestScssView,
    meta: { index: 100, title: 'SCSS组件测试', hidden: true }
  },
]

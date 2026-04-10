import { useRouter } from 'vue-router'
import { usePageTransition } from './usePageTransition'

/**
 * 1级页面滚轮导航逻辑
 * 支持线性连续跳转：首页 → 文章 → 关于 → 留言
 */
export function usePrimaryPageWheel(currentRouteName) {
  const router = useRouter()
  const { isAnimating } = usePageTransition()

  // 定义1级页面的线性顺序
  const pageOrder = [
    'home',           // 首页
    'posts-immersive', // 文章
    'about-immersive', // 关于  
    'message-immersive' // 留言
  ]

  // 获取当前页面在顺序中的索引
  const currentIndex = pageOrder.indexOf(currentRouteName)

  const handleWheel = (e) => {
    if (isAnimating.value) return
    
    e.preventDefault()

    // 滚轮向上：返回前一个页面（如果存在）
    if (e.deltaY < 0 && currentIndex > 0) {
      const prevPage = pageOrder[currentIndex - 1]
      router.push(getPageRoutePath(prevPage))
    }
    // 滚轮向下：跳转到下一个页面（如果存在）
    else if (e.deltaY > 0 && currentIndex < pageOrder.length - 1) {
      const nextPage = pageOrder[currentIndex + 1]
      router.push(getPageRoutePath(nextPage))
    }
  }

  // 根据路由名称获取对应的路径
  const getPageRoutePath = (routeName) => {
    const routeMap = {
      'home': '/',
      'posts-immersive': '/posts-immersive',
      'about-immersive': '/about-immersive',
      'message-immersive': '/message-immersive'
    }
    return routeMap[routeName] || '/'
  }

  return { handleWheel }
}
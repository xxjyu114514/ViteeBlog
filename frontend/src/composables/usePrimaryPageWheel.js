import { useRouter } from 'vue-router'
import { usePageTransition } from './usePageTransition'

export function usePrimaryPageWheel(currentRouteName) {
  const router = useRouter()
  const { isAnimating } = usePageTransition()

  const pageOrder = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']
  const currentIndex = pageOrder.indexOf(currentRouteName)

  const handleWheel = (e) => {
    // 1. 如果正在执行“打断”后的跳转，严格拦截，防止双重触发
    if (window._isBreaking) return 

    const isScrollingUp = e.deltaY < 0
    const isScrollingDown = e.deltaY > 0

    // 2. 向下滚动锁：如果正在动画，禁止向下多跳
    if (isAnimating.value && isScrollingDown) return

    e.preventDefault()

    // --- 向上滚动：打断并强制返回 ---
    if (isScrollingUp && currentIndex > 0) {
      // 开启全局打断锁，防止滚轮动能触发多次 handleWheel
      window._isBreaking = true 
      
      // 暴力重置动画状态，允许路由立即变更
      isAnimating.value = false 
      
      const prevPage = pageOrder[currentIndex - 1]
      router.push(getPageRoutePath(prevPage))

      // 在页面跳转后的一段时间内，保持锁定，等待路由彻底卸载
      setTimeout(() => {
        window._isBreaking = false
      }, 500) 
    }
    // --- 向下滚动：正常步进 ---
    else if (isScrollingDown && currentIndex < pageOrder.length - 1) {
      const nextPage = pageOrder[currentIndex + 1]
      router.push(getPageRoutePath(nextPage))
    }
  }

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
import { useRouter } from 'vue-router'
import { usePageTransition } from './usePageTransition'

let isBreaking = false

export function usePrimaryPageWheel(currentRouteName) {
  const router = useRouter()
  const { isAnimating } = usePageTransition()

  const pageOrder = ['home', 'posts-immersive', 'about-immersive', 'message-immersive']
  const currentIndex = pageOrder.indexOf(currentRouteName)

  const handleWheel = (e) => {
    if (isBreaking) return

    const isScrollingUp = e.deltaY < 0
    const isScrollingDown = e.deltaY > 0

    if (isAnimating.value && isScrollingDown) return

    e.preventDefault()

    if (isScrollingUp && currentIndex > 0) {
      isBreaking = true
      isAnimating.value = false
      const prevPage = pageOrder[currentIndex - 1]
      router.push(getPageRoutePath(prevPage))
      setTimeout(() => { isBreaking = false }, 500)
    }
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
      'message-immersive': '/message-immersive',
    }
    return routeMap[routeName] || '/'
  }

  return { handleWheel }
}

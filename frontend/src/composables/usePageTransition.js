import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const IMMERSIVE_ROUTE_NAMES = new Set([
  'home',
  'posts-immersive',
  'about-immersive',
  'message-immersive'
])

const isAnimating = ref(false)
let prevRoute = null
let prevRouteIndex = 0

export function usePageTransition() {
  const router = useRouter()

  const slideOptions = {
    duration: 800,
    easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    fill: 'forwards',
  }

  const fadeOptions = {
    duration: 300,
    easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    fill: 'forwards',
  }

  const getIndex = (route) => route?.meta?.index ?? 0
  const isImmersive = (route) => IMMERSIVE_ROUTE_NAMES.has(route?.name)

  onMounted(() => {
    if (!prevRoute) {
      prevRoute = router.currentRoute.value
      prevRouteIndex = getIndex(prevRoute)
    }
  })

  const onEnter = (el, done) => {
    isAnimating.value = true
    const toRoute = router.currentRoute.value
    const fromRoute = prevRoute

    const toImmersive = isImmersive(toRoute)
    const fromImmersive = isImmersive(fromRoute)
    const bothImmersive = toImmersive && fromImmersive

    const toIndex = getIndex(toRoute)
    const fromIndex = getIndex(fromRoute)
    const isBackward = toIndex < fromIndex

    let animation

    if (bothImmersive) {
      if (isBackward) {
        el.style.zIndex = 1
        animation = el.animate([{ opacity: 0.8 }, { opacity: 1 }], slideOptions)
      } else {
        el.style.zIndex = 10
        animation = el.animate([
          { clipPath: 'inset(0 0 0 100%)' },
          { clipPath: 'inset(0 0 0 0%)' }
        ], slideOptions)
      }
    } else {
      el.style.zIndex = 10
      animation = el.animate([{ opacity: 0 }, { opacity: 1 }], fadeOptions)
    }

    animation.onfinish = () => {
      done()
      setTimeout(() => { isAnimating.value = false }, 200)
    }

    prevRoute = toRoute
    prevRouteIndex = toIndex
  }

  const onLeave = (el, done) => {
    const toRoute = router.currentRoute.value
    const fromRoute = prevRoute

    const toImmersive = isImmersive(toRoute)
    const fromImmersive = isImmersive(fromRoute)
    const bothImmersive = toImmersive && fromImmersive

    const toIndex = getIndex(toRoute)
    const fromIndex = getIndex(fromRoute)
    const isBackward = toIndex < fromIndex

    let animation

    if (bothImmersive) {
      if (isBackward) {
        el.style.zIndex = 10
        animation = el.animate([
          { clipPath: 'inset(0 0 0 0%)' },
          { clipPath: 'inset(0 0 0 100%)' }
        ], slideOptions)
      } else {
        el.style.zIndex = 1
        animation = el.animate([{ opacity: 1 }, { opacity: 0.6 }], slideOptions)
      }
    } else {
      el.style.zIndex = 1
      animation = el.animate([{ opacity: 1 }, { opacity: 0 }], fadeOptions)
    }

    animation.onfinish = done
  }

  return { onEnter, onLeave, isAnimating }
}

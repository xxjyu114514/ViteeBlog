import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const isAnimating = ref(false)
let prevRouteIndex = 0

export function usePageTransition() {
  const router = useRouter()

  const animOptions = {
    duration: 800,
    easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    fill: 'forwards',
  }

  const getIndex = (route) => route?.meta?.index ?? 0

  onMounted(() => {
    if (!prevRouteIndex) {
      prevRouteIndex = getIndex(router.currentRoute.value)
    }
  })

  const onEnter = (el, done) => {
    isAnimating.value = true
    const toIndex = getIndex(router.currentRoute.value)
    const fromIndex = prevRouteIndex || 0
    const isBackward = toIndex < fromIndex

    let animation
    if (isBackward) {
      el.style.zIndex = 1
      animation = el.animate([
        { opacity: 0.8 },
        { opacity: 1 },
      ], animOptions)
    } else {
      el.style.zIndex = 10
      animation = el.animate([
        { clipPath: 'inset(0 0 0 100%)' },
        { clipPath: 'inset(0 0 0 0%)' },
      ], animOptions)
    }

    animation.onfinish = () => {
      done()
      setTimeout(() => { isAnimating.value = false }, 200)
    }

    prevRouteIndex = toIndex
  }

  const onLeave = (el, done) => {
    const toIndex = getIndex(router.currentRoute.value)
    const fromIndex = prevRouteIndex || 0
    const isBackward = toIndex < fromIndex

    let animation
    if (isBackward) {
      el.style.zIndex = 10
      animation = el.animate([
        { clipPath: 'inset(0 0 0 0%)' },
        { clipPath: 'inset(0 0 0 100%)' },
      ], animOptions)
    } else {
      el.style.zIndex = 1
      animation = el.animate([
        { opacity: 1 },
        { opacity: 0.6 },
      ], animOptions)
    }
    animation.onfinish = done
  }

  return { onEnter, onLeave, isAnimating }
}

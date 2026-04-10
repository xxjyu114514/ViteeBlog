import { ref } from 'vue'
import { useRouter } from 'vue-router'

const isAnimating = ref(false)

export function usePageTransition() {
  const router = useRouter()
  
  const animOptions = {
    duration: 800,
    easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    fill: 'forwards'
  }

  // 获取当前路由索引的辅助函数
  const getIndex = (route) => route?.meta?.index ?? 0

  /**
   * 进入动画
   */
  const onEnter = (el, done) => {
    isAnimating.value = true
    
    // 【核心修复】：实时获取去往(to)和来自(from)的索引
    const toIndex = getIndex(router.currentRoute.value)
    // 注意：这里需要通过 router 的历史记录判断，或者简单的逻辑判断
    // 由于 vue-router 在 transition 中执行 onEnter 时，currentRoute 已经是新路由了
    // 我们需要记录上一次的索引
    const fromIndex = window._prevRouteIndex || 0
    
    const isBackward = toIndex < fromIndex
    
    let animation;
    if (isBackward) {
      // 后退动画：新页面从左侧（-10%）稍微淡入，层级在下
      el.style.zIndex = 1
      animation = el.animate([
        { opacity: 0.8 },
        { opacity: 1 }
      ], animOptions)
    } else {
      // 前进动画：新页面从右侧切入，层级在上
      el.style.zIndex = 10
      animation = el.animate([
        { clipPath: 'inset(0 0 0 100%)' },
        { clipPath: 'inset(0 0 0 0%)' }
      ], animOptions)
    }

    animation.onfinish = () => {
      done()
      setTimeout(() => { isAnimating.value = false }, 200)
    }
    
    // 更新“上一次”的索引，供下次使用
    window._prevRouteIndex = toIndex
  }

  /**
   * 离开动画
   */
  const onLeave = (el, done) => {
    const toIndex = getIndex(router.currentRoute.value)
    const fromIndex = window._prevRouteIndex || 0
    const isBackward = toIndex < fromIndex

    let animation;
    if (isBackward) {
      // 后退动画：旧页面向右侧擦除消失
      el.style.zIndex = 10
      animation = el.animate([
        { clipPath: 'inset(0 0 0 0%)' },
        { clipPath: 'inset(0 0 0 100%)' }
      ], animOptions)
    } else {
      // 前进动画：旧页面向左微移并变暗
      el.style.zIndex = 1
      animation = el.animate([
        { opacity: 1 },
        { opacity: 0.6 }
      ], animOptions)
    }
    animation.onfinish = done
  }

  return { onEnter, onLeave, isAnimating }
}
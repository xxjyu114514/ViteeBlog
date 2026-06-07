import { ref, onMounted, onUnmounted } from 'vue'

export function useTilt3D(config = {}) {
  const {
    maxRotate = 5,
    perspective = 800,
    defaultRotateX = 0,
    enableX = true,
    enableY = true,
    resetOnLeave = true,
    resetDuration = 200,
    leftDefaultY = 15,
    rightDefaultY = -15,
  } = config

  let elements = []
  let rafId = null
  let mouseX = 0
  let mouseY = 0
  let ticking = false
  let resetTimer = null

  const updateTilt = () => {
    if (!elements.length) return

    const centerX = window.innerWidth / 2
    const centerY = window.innerHeight / 2

    let normX = (mouseX - centerX) / centerX
    let normY = (mouseY - centerY) / centerY
    normX = Math.min(Math.max(normX, -1), 1)
    normY = Math.min(Math.max(normY, -1), 1)

    const mouseRotateX = -normY * maxRotate
    const mouseRotateY = normX * maxRotate

    elements.forEach(el => {
      const isLeft = el.classList.contains('profile-card')
      const isRight = el.classList.contains('pc-right')

      let defaultY = 0
      if (isLeft) defaultY = leftDefaultY
      if (isRight) defaultY = rightDefaultY

      let rotateX = defaultRotateX
      let rotateY = defaultY

      if (enableX) rotateX += mouseRotateX
      if (enableY) rotateY += mouseRotateY

      el.style.transform = `perspective(${perspective}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
    })
  }

  const onMouseMove = (e) => {
    mouseX = e.clientX
    mouseY = e.clientY
    if (!ticking) {
      rafId = requestAnimationFrame(() => {
        updateTilt()
        ticking = false
      })
      ticking = true
    }
  }

  const resetTilt = () => {
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    ticking = false

    if (!resetOnLeave) return
    if (resetTimer) cancelAnimationFrame(resetTimer)

    const items = elements.map(el => {
      const isLeft = el.classList.contains('profile-card')
      const isRight = el.classList.contains('pc-right')
      let defaultY = 0
      if (isLeft) defaultY = leftDefaultY
      if (isRight) defaultY = rightDefaultY

      const transform = el.style.transform
      const matchX = transform?.match(/rotateX\(([-\d.]+)deg\)/)
      const matchY = transform?.match(/rotateY\(([-\d.]+)deg\)/)
      const startX = matchX ? parseFloat(matchX[1]) : defaultRotateX
      const startY = matchY ? parseFloat(matchY[1]) : defaultY

      return { el, startX, startY, targetX: defaultRotateX, targetY: defaultY }
    })

    const startTime = performance.now()

    const animateReset = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(1, elapsed / resetDuration)
      const easeProgress = 1 - Math.pow(1 - progress, 3)

      items.forEach(({ el, startX, startY, targetX, targetY }) => {
        const currentX = startX + (targetX - startX) * easeProgress
        const currentY = startY + (targetY - startY) * easeProgress
        el.style.transform = `perspective(${perspective}px) rotateX(${currentX}deg) rotateY(${currentY}deg)`
      })

      if (progress < 1) {
        resetTimer = requestAnimationFrame(animateReset)
      } else {
        resetTimer = null
      }
    }

    resetTimer = requestAnimationFrame(animateReset)
  }

  const init = () => {
    elements = Array.from(document.querySelectorAll('.tilt-target'))
    if (!elements.length) return

    mouseX = window.innerWidth / 2
    mouseY = window.innerHeight / 2
    updateTilt()

    window.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseleave', resetTilt)
  }

  const destroy = () => {
    window.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseleave', resetTilt)
    if (rafId) cancelAnimationFrame(rafId)
    if (resetTimer) cancelAnimationFrame(resetTimer)
    elements.forEach(el => { el.style.transform = '' })
  }

  return { init, destroy }
}

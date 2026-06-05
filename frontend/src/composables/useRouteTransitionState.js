/**
 * 共享路由过渡状态
 * 用于 posts-immersive ↔ posts 之间的双向动画协调
 */
const _lastFromRoute = { value: null }

export function useRouteTransitionState() {
  /** 记录进入当前页面之前的来源路由名 */
  const setLastFromRoute = (name) => { _lastFromRoute.value = name }
  const getLastFromRoute = () => _lastFromRoute.value

  return { setLastFromRoute, getLastFromRoute }
}

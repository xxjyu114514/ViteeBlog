/**
 * useApi — 通用 API 调用包装
 *
 * 消除全部 38 个 API 方法中重复的 try-catch-loading 模板。
 * 提供 { data, loading, error, execute } 标准格式。
 *
 * @template T
 * @param {Function|string} fetcher - 异步函数或 service 方法名
 * @param {...any} args - 传给 fetcher 的参数
 * @returns {{ data: import('vue').Ref<T|null>, loading: import('vue').Ref<boolean>, error: import('vue').Ref<string|null>, submitLock: import('vue').Ref<boolean>, execute: Function }}
 */
import { ref, readonly } from 'vue'

export function useApi(fetcher, ...args) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const submitLock = ref(false)

  const execute = async (...callArgs) => {
    // 检查最后一个参数是否为 options，从中读取 method
    const lastArg = callArgs.length > 0 ? callArgs[callArgs.length - 1] : null
    const isQuery = lastArg?.method === 'GET' || lastArg?.method === undefined

    // 非查询请求（POST/PUT/DELETE）受提交锁保护
    if (!isQuery && submitLock.value) return null

    loading.value = true
    if (!isQuery) submitLock.value = true
    error.value = null

    try {
      const fn = typeof fetcher === 'function' ? fetcher : null
      if (!fn) throw new Error('useApi: 缺少 fetcher 函数')

      const result = await fn(...callArgs)

      if (!result || !result.success) {
        error.value = result?.message || '操作失败'
        return null
      }

      data.value = result.data ?? null
      return data.value
    } catch (err) {
      console.error('[useApi] 请求异常:', err)
      error.value = '网络连接异常，请稍后重试'
      return null
    } finally {
      loading.value = false
      if (!isQuery) submitLock.value = false
    }
  }

  // 如果传入了初始参数，立即执行
  if (args.length > 0) {
    execute(...args)
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    submitLock: readonly(submitLock),
    execute,
  }
}

/**
 * useApiSubmit — 适用于表单提交场景（不需要 data 响应式）
 * 简化了返回结构
 */
export function useApiSubmit() {
  const loading = ref(false)
  const error = ref(null)
  const submitLock = ref(false)

  const execute = async (fetcher, ...args) => {
    if (submitLock.value) return { success: false, message: '操作进行中...' }

    loading.value = true
    submitLock.value = true
    error.value = null

    try {
      const result = await fetcher(...args)
      if (!result || !result.success) {
        error.value = result?.message || '操作失败'
        return { success: false, message: error.value }
      }
      return { success: true, data: result.data }
    } catch (err) {
      console.error('[useApiSubmit] 请求异常:', err)
      error.value = '网络连接异常'
      return { success: false, message: '网络连接异常' }
    } finally {
      loading.value = false
      submitLock.value = false
    }
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    submitLock: readonly(submitLock),
    execute,
  }
}

import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { getBaseUrl, API_TIMEOUT } from './config'

/**
 * 统一错误提取与语义化处理
 * 将后端的报错翻译成人类友好的 UI 提示
 */
export const handleFriendlyError = (error, context = '操作') => {
  // 网络断开或完全没有响应
  if (!error) return `${context}失败，请检查网络连接`
  
  // 优先使用后端返回的具体业务 detail 字段
  if (error.data && error.data.detail) {
    return error.data.detail
  }

  // HTTP 状态码兜底映射
  const statusMap = {
    400: '请求参数有误，请检查后重试',
    401: '登录已过期，请重新登录',
    403: '您没有权限执行此操作',
    404: '请求的资源不存在',
    408: '请求超时，请稍后再试',
    409: '文章已被他人修改，请刷新后重新编辑', // 乐观锁冲突
    422: '数据格式校验失败',
    429: '操作过于频繁，请稍后再试', // 请求限流
    500: '服务器繁忙，请稍后重试',
    502: '网关错误，服务暂时不可用'
  }
  
  return statusMap[error.status] || `${context}失败，请稍后重试 (${error.status || '未知错误'})`
}

/**
 * 全局单例的 Fetch 客户端
 */
export const useBaseFetch = createFetch({
  baseUrl: getBaseUrl(),
  options: {
    timeout: API_TIMEOUT,
    // 请求前拦截：统一注入 Token
    async beforeFetch({ options, url }) {
      const userStore = useUserStore()
      if (userStore.token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${userStore.token}`
        }
      }
      return { options, url }
    },
    // 请求后拦截：统一处理 401 登出等全局行为
    onFetchError(ctx) {
      // 改进逻辑：排除登录请求的401错误
      if (ctx.response?.status === 401) {
        // 检查是否为登录请求（排除/auth/login路径）
        const requestUrl = ctx.request?.url || '';
        if (!requestUrl.includes('/auth/login')) {
          const userStore = useUserStore()
          userStore.logout()
          // 强制重定向到登录页
          window.location.href = '/login'
        }
      }
      return ctx
    }
  },
  fetchOptions: {
    mode: 'cors'
  }
})
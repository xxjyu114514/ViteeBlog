import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { getBaseUrl } from '@/config/apiConfig'
import { buildUrl } from '@/utils/apiUtils'

// 创建一个预配置的 fetch 实例
const useBaseFetch = createFetch({
  baseUrl: getBaseUrl(),
  options: {
    async beforeFetch({ options }) {
      const userStore = useUserStore()
      if (userStore.token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${userStore.token}`,
        }
      }
      return { options }
    },
    onFetchError(ctx) {
      // 全局处理：例如 401 自动登出
      if (ctx.response?.status === 401) {
        const userStore = useUserStore()
        const router = useRouter()
        userStore.logout()
        // 使用 Vue Router 跳转而不是 window.location
        router.push('/login')
      }
      return ctx
    },
  },
  fetchOptions: {
    mode: 'cors',
  },
})

// 统一的错误信息提取函数
const extractFriendlyErrorMessage = (error, context = '操作') => {
  // 开发者调试信息（保留详细错误）
  if (error) {
    console.error(`🐛 ${context}错误详情:`, {
      status: error.status,
      message: error.message,
      data: error.data,
      url: error.url
    })
  }
  
  // 用户友好提示
  if (!error) {
    return `${context}失败，请稍后重试`
  }
  
  // 优先使用后端返回的具体错误详情
  if (error.data?.detail) {
    return error.data.detail
  }
  
  // 根据HTTP状态码提供友好提示
  switch (error.status) {
    case 400:
      return '输入信息有误，请检查后重试'
    case 401:
      return '身份验证失败，请检查用户名和密码'
    case 403:
      if (error.data?.detail && error.data.detail.includes('锁定')) {
        return error.data.detail // 保留具体的锁定时间信息
      }
      return '操作被拒绝，请稍后重试'
    case 404:
      return '请求的资源不存在'
    case 429:
      return '操作太频繁，请稍后再试'
    case 500:
      return '系统繁忙，请稍后重试'
    case 502:
    case 503:
    case 504:
      return '服务暂时不可用，请稍后重试'
    default:
      return `${context}失败，请稍后重试`
  }
}

export function useAuthAPI() {
  const userStore = useUserStore()
  const router = useRouter()

  // 登录逻辑
  const login = async (username, password) => {
    const { data, error } = await useBaseFetch('/auth/login').post({
      username,
      password,
    }).json()

    if (!error.value && data.value) {
      userStore.setAuth(data.value.access_token, data.value.user)
      return { success: true }
    }
    
    // 使用友好的错误信息
    const errorMessage = extractFriendlyErrorMessage(error.value, '登录')
    return { success: false, message: errorMessage }
  }

  // 注册逻辑
  const register = async (userData) => {
    const { data, error } = await useBaseFetch('/auth/register').post(userData).json()
    
    if (!error.value) {
      return { data, error }
    }
    
    // 修改错误对象，添加友好的错误信息
    error.value = {
      ...error.value,
      friendlyMessage: extractFriendlyErrorMessage(error.value, '注册')
    }
    
    return { data, error }
  }

  // 发送注册验证码
  const sendRegisterCode = async (email) => {
    const { data, error } = await useBaseFetch('/auth/send-register-code').post({ email }).json()
    
    if (!error.value) {
      return { data, error }
    }
    
    // 修改错误对象，添加友好的错误信息
    error.value = {
      ...error.value,
      friendlyMessage: extractFriendlyErrorMessage(error.value, '发送验证码')
    }
    
    return { data, error }
  }

  return { login, register, sendRegisterCode }
}
import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
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
        userStore.logout()
        // 在composable中不能使用useRouter，改用window.location
        window.location.href = '/login'
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
      return '身份验证失败，请重新登录'
    case 403:
      return '权限不足'
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

export function useMetaAPI() {
  const userStore = useUserStore()

  // 获取分类列表
  const getCategories = async () => {
    const { data, error } = await useBaseFetch('/meta/categories').get().json()
    
    if (!error.value) {
      // 安全检查：确保data.value存在，元数据接口通常返回数组
      const categoriesData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: categoriesData }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取分类')
    return { success: false, message: errorMessage }
  }

  // 获取标签列表
  const getTags = async () => {
    const { data, error } = await useBaseFetch('/meta/tags').get().json()
    
    if (!error.value) {
      // 安全检查：确保data.value存在，元数据接口通常返回数组
      const tagsData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: tagsData }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取标签')
    return { success: false, message: errorMessage }
  }

  return { getCategories, getTags }
}
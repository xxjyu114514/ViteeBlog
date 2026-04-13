import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

// 创建一个预配置的 fetch 实例
const useBaseFetch = createFetch({
  baseUrl: 'http://127.0.0.1:8000/api/v1',
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
    
    // 更准确地提取错误信息
    let errorMessage = '登录失败'
    if (error.value) {
      // 尝试从不同位置获取错误详情
      if (error.value.data?.detail) {
        errorMessage = error.value.data.detail
      } else if (error.value.message) {
        errorMessage = error.value.message
      } else if (typeof error.value === 'string') {
        errorMessage = error.value
      } else {
        errorMessage = `HTTP ${error.value.status || '未知错误'}`
      }
    }
    return { success: false, message: errorMessage }
  }

  // 注册逻辑
  const register = async (userData) => {
    return useBaseFetch('/auth/register').post(userData).json()
  }

  return { login, register }
}
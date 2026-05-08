import { useUserStore } from '@/stores/user'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useAuthAPI() {
  const userStore = useUserStore()

  const login = async (username, password) => {
    const url = buildUrl('/auth/login')
    // 发送 FormData (假设后端使用 OAuth2 Password 模式)
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const { data, error } = await useBaseFetch(url).post(formData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '登录') }
    }
    
    // 登录成功后更新 Store
    if (data.value) {
      userStore.setAuth(data.value.access_token, data.value.user)
    }
    
    return { success: true, data: data.value }
  }

  const register = async (userData) => {
    const url = buildUrl('/auth/register')
    const { data, error } = await useBaseFetch(url).post(userData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '注册') }
    }
    return { success: true, data: data.value }
  }

  const getCurrentUser = async () => {
    const url = buildUrl('/auth/me')
    const { data, error } = await useBaseFetch(url).get().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取用户信息') }
    }
    return { success: true, data: data.value }
  }

  const logout = async () => {
    const url = buildUrl('/auth/logout')
    const { data, error } = await useBaseFetch(url).post().json()

    // 无论后端是否成功，前端都执行登出逻辑
    userStore.logout()

    if (error.value) {
      // 可以选择忽略登出接口的错误，或者返回提示
      return { success: false, message: handleFriendlyError(error.value, '登出') }
    }
    return { success: true, data: data.value }
  }

  return { login, register, getCurrentUser, logout }
}
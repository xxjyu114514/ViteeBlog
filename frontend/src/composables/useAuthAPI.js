import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useAuthAPI() {
  const userStore = useUserStore()
  // 认证操作的loading状态
  const authLoading = ref(false)
  // 防重复提交锁
  const authSubmitLock = ref(false)

  const login = async (username, password) => {
    if (authSubmitLock.value) {
      return { success: false, message: '登录正在进行中，请稍后...' }
    }
    
    authLoading.value = true
    authSubmitLock.value = true
    
    try {
      const url = buildUrl('/auth/login')
      // 发送 JSON 格式数据，匹配后端 Pydantic UserLogin 模型
      const loginData = {
        username: username,
        password: password
      }

      // 关键修改：使用 updateDataOnError: true 来捕获错误响应
      const fetchInstance = useBaseFetch(url, {
        updateDataOnError: true
      });
      
      const { data, error } = await fetchInstance.post(loginData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '登录') }
      }
      
      // 登录成功后更新 Store
      if (data.value) {
        userStore.setAuth(data.value.access_token, data.value.user)
      }
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('login error:', err)
      return { success: false, message: '登录时发生未知错误，请稍后重试' }
    } finally {
      authLoading.value = false
      authSubmitLock.value = false
    }
  }

  const register = async (registerData) => {
    if (authSubmitLock.value) {
      return { success: false, message: '注册正在进行中，请稍后...' }
    }
    
    authLoading.value = true
    authSubmitLock.value = true
    
    try {
      // registerData 应该已经是完整的请求体格式: { user_in: {...}, email_code: "..." }
      const url = buildUrl('/auth/register')
      const { data, error } = await useBaseFetch(url).post(registerData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '注册') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('register error:', err)
      return { success: false, message: '注册时发生未知错误，请稍后重试' }
    } finally {
      authLoading.value = false
      authSubmitLock.value = false
    }
  }

  // 发送注册验证码
  const sendRegisterCode = async (email) => {
    if (authSubmitLock.value) {
      return { success: false, message: '验证码发送中，请稍后...' }
    }
    
    authLoading.value = true
    authSubmitLock.value = true
    
    try {
      const url = buildUrl('/auth/send-register-code')
      // 关键修改：使用 updateDataOnError: true 来捕获错误响应
      const fetchInstance = useBaseFetch(url, {
        updateDataOnError: true
      });
      
      const { data, error } = await fetchInstance.post({ email }).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '发送验证码') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('sendRegisterCode error:', err)
      return { success: false, message: '发送验证码时发生未知错误，请稍后重试' }
    } finally {
      authLoading.value = false
      authSubmitLock.value = false
    }
  }

  const getCurrentUser = async () => {
    authLoading.value = true
    
    try {
      const url = buildUrl('/auth/me')
      // 关键修改：使用 updateDataOnError: true 来捕获错误响应
      const fetchInstance = useBaseFetch(url, {
        updateDataOnError: true
      });
      
      const { data, error } = await fetchInstance.get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取用户信息') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('getCurrentUser error:', err)
      return { success: false, message: '获取用户信息时发生未知错误，请稍后重试' }
    } finally {
      authLoading.value = false
    }
  }

  const logout = async () => {
    authLoading.value = true
    
    try {
      const url = buildUrl('/auth/logout')
      // 关键修改：使用 updateDataOnError: true 来捕获错误响应
      const fetchInstance = useBaseFetch(url, {
        updateDataOnError: true
      });
      
      const { data, error } = await fetchInstance.post().json()

      // 无论后端是否成功，前端都执行登出逻辑
      userStore.logout()

      if (error.value) {
        // 可以选择忽略登出接口的错误，或者返回提示
        return { success: false, message: handleFriendlyError(error.value, '登出') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('logout error:', err)
      // 即使登出失败，用户状态也已清除
      return { success: true, message: '已退出登录' }
    } finally {
      authLoading.value = false
    }
  }

  return { 
    login, 
    register, 
    sendRegisterCode,
    getCurrentUser, 
    logout,
    // 新增的loading状态和提交锁
    authLoading,
    authSubmitLock
  }
}
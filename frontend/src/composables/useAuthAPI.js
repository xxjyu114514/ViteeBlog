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
    console.log('🔍 DEBUG: 开始登录请求', { username })
    const { data, error } = await useBaseFetch('/auth/login').post({
      username,
      password,
    }).json()

    if (!error.value && data.value) {
      userStore.setAuth(data.value.access_token, data.value.user)
      console.log('✅ DEBUG: 登录成功', data.value)
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
    console.error('❌ DEBUG: 登录失败', error.value, errorMessage)
    return { success: false, message: errorMessage }
  }

  // 注册逻辑
  const register = async (userData) => {
    console.log('🔍 DEBUG: 开始注册请求', userData)
    const { data, error } = await useBaseFetch('/auth/register')
      .post(userData)
      .json()

    if (!error.value && data.value) {
      console.log('✅ DEBUG: 注册成功', data.value)
      return { success: true, data: data.value }
    }
    
    let errorMessage = '注册失败'
    if (error.value) {
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
    console.error('❌ DEBUG: 注册失败', error.value, errorMessage)
    return { success: false, message: errorMessage }
  }

  /**
   * 发送邮箱验证码
   * @param {string} email - 用户邮箱
   * @returns {Promise<Object>} - 响应结果
   */
  const sendVerificationCode = async (email) => {
    console.log('🔍 DEBUG: 开始发送验证码请求', { email })
    const { data, error } = await useBaseFetch('/auth/send-code')
      .post({ email })
      .json()

    if (!error.value && data.value) {
      console.log('✅ DEBUG: 验证码发送成功', data.value)
      return { success: true, data: data.value }
    }
    
    let errorMessage = '发送验证码失败'
    if (error.value) {
      console.error('❌ DEBUG: 发送验证码时发生错误', error.value)
      if (error.value.data?.detail) {
        errorMessage = error.value.data.detail
      } else if (error.value.message) {
        errorMessage = error.value.message
      } else if (error.value.status === 404) {
        errorMessage = '服务器未找到该接口，请检查后端服务是否正常运行'
      } else if (error.value.status === 429) {
        errorMessage = '发送太频繁，请稍后再试'
      } else if (error.value.status === 500) {
        errorMessage = '服务器内部错误，请稍后再试'
      }
    }
    console.error('❌ DEBUG: 验证码发送最终失败消息', errorMessage)
    return { success: false, message: errorMessage }
  }

  /**
   * 验证邮箱验证码
   * @param {Object} payload - { email, code }
   * @returns {Promise<Object>} - 验证结果
   */
  const verifyEmailCode = async (payload) => {
    console.log('🔍 DEBUG: 开始验证码校验请求', payload)
    console.log('📊 DEBUG: 发送的请求数据 - email:', payload.email, 'code:', payload.code, 'code类型:', typeof payload.code, 'code长度:', payload.code.length)
    
    const { data, error } = await useBaseFetch('/auth/verify-code')
      .post(payload)
      .json()

    if (!error.value && data.value) {
      console.log('✅ DEBUG: 验证码校验成功', data.value)
      return { success: true, data: data.value }
    }
    
    let errorMessage = '验证码校验失败'
    if (error.value) {
      console.error('❌ DEBUG: 验证码校验时发生错误', error.value)
      if (error.value.data?.detail) {
        errorMessage = error.value.data.detail
      } else if (error.value.message) {
        errorMessage = error.value.message
      }
    }
    console.error('❌ DEBUG: 验证码校验最终失败消息', errorMessage)
    return { success: false, message: errorMessage }
  }

  return { 
    login, 
    register,
    sendVerificationCode,
    verifyEmailCode
  }
}
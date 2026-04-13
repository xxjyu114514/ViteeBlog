import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态定义
  const token = ref(localStorage.getItem('vitee_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('vitee_user')) || null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  // Actions: 设置认证信息
  function setAuth(accessToken, user) {
    token.value = accessToken
    userInfo.value = user
    localStorage.setItem('vitee_token', accessToken)
    localStorage.setItem('vitee_user', JSON.stringify(user))
  }

  // Actions: 清除登录状态
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('vitee_token')
    localStorage.removeItem('vitee_user')
  }

  return { 
    token, 
    userInfo, 
    isAuthenticated, 
    isAdmin, 
    setAuth, 
    logout 
  }
})
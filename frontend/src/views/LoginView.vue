<template>
  <div class="login-page">
    <div class="login-visual">
      <div class="bg-wrapper">
        <img src="../assets/login-bg.webp" alt="Background" class="bg-image" />
        <div class="top-shadow-overlay"></div>
      </div>
      
      <div class="visual-content">
        <transition name="text-move" mode="out-in">
          <div class="brand-info" :key="isLogin ? 'login-title' : 'reg-title'">
            <h1>{{ isLogin ? '观测笔记' : '加入观测' }}</h1>
            <div class="animated-bar"></div>
            <p>DESIGN FOR OBSERVATION / 2026</p>
          </div>
        </transition>
      </div>
    </div>

    <div class="login-form-container">
      <transition name="form-stagger" mode="out-in">
        <div class="form-card" :key="isLogin ? 'login-card' : 'reg-card'">
          <header class="form-header">
            <h2>{{ isLogin ? '登 录' : '注 册' }}</h2>
            <p>{{ isLogin ? '博主账号身份验证' : '注册普通用户以发表评论' }}</p>
          </header>

          <!-- 错误提示区域 -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <!-- 成功提示区域 -->
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>

          <form @submit.prevent="handleSubmit" class="main-form">
            <div class="input-group">
              <label>账号</label>
              <input 
                v-model="formData.username" 
                type="text" 
                placeholder="Username" 
                required 
                @input="clearMessages"
              />
            </div>

            <div v-if="!isLogin" class="input-group email-with-send">
              <label>电子邮箱</label>
              <div class="email-input-wrapper">
                <input 
                  v-model="formData.email" 
                  type="email" 
                  placeholder="Email Address" 
                  required 
                  @input="clearMessages"
                />
                <button 
                  type="button" 
                  class="send-code-btn"
                  :disabled="isSendingCode || !isValidEmail(formData.email)"
                  @click="sendVerificationCode"
                >
                  {{ isSendingCode ? '发送中...' : '发送验证码' }}
                </button>
              </div>
            </div>

            <div v-if="!isLogin" class="input-group">
              <label>邮箱验证码</label>
              <input 
                v-model="formData.verificationCode" 
                type="text" 
                placeholder="请输入邮箱验证码" 
                required 
                @input="clearMessages"
              />
            </div>

            <div class="input-group">
              <label>密码</label>
              <input 
                v-model="formData.password" 
                type="password" 
                placeholder="Password" 
                required 
                @input="clearMessages"
              />
            </div>

            <div class="form-options">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.remember" />
                <span class="custom-check"></span>
                <span>记住密码</span>
              </label>
              <a v-if="isLogin" href="#" class="forgot-link">忘记密码？</a>
            </div>

            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="!isSubmitting">{{ isLogin ? '立即登录' : '提交注册' }}</span>
              <span v-else>请求中...</span>
            </button>
          </form>

          <div class="switch-area">
            <span>{{ isLogin ? '没有账号?' : '已有账号?' }}</span>
            <button @click="toggleMode" class="btn-toggle">
              {{ isLogin ? '去注册' : '去登录' }}
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthAPI } from '@/composables/useAuthAPI'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const authAPI = useAuthAPI()
const userStore = useUserStore()
const isLogin = ref(true)
const isSubmitting = ref(false)
const isSendingCode = ref(false) // 新增：发送验证码状态
const errorMessage = ref('')
const successMessage = ref('')

// 响应式表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  verificationCode: '',
  remember: false
})

// 验证邮箱格式
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  clearMessages()
}

const clearMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

// 发送验证码功能
const sendVerificationCode = async () => {
  if (!isValidEmail(formData.email)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  isSendingCode.value = true
  errorMessage.value = ''
  
  try {
    const { data, error } = await authAPI.sendRegisterCode(formData.email)
    
    if (!error.value && data.value) {
      successMessage.value = '验证码已发送至您的邮箱，请注意查收'
      // 3秒后自动清除成功提示
      setTimeout(() => {
        if (successMessage.value === '验证码已发送至您的邮箱，请注意查收') {
          successMessage.value = ''
        }
      }, 3000)
    } else {
      // 使用友好的错误信息
      const errorMsg = error.value?.friendlyMessage || '发送验证码失败，请稍后重试'
      errorMessage.value = errorMsg
    }
  } catch (error) {
    console.error('发送验证码异常:', error)
    errorMessage.value = '网络连接异常，请检查网络后重试'
  } finally {
    isSendingCode.value = false
  }
}

/**
 * 核心修改：使用 useAuthAPI 替代原生 fetch，并调用 userStore.setAuth
 */
const handleSubmit = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true
  clearMessages()

  try {
    if (isLogin.value) {
      // 登录逻辑
      console.log('开始登录请求，用户名:', formData.username)
      const result = await authAPI.login(formData.username, formData.password)
      
      if (result.success) {
        // 登录成功：userStore.setAuth 已在 useAuthAPI 内部调用
        console.log('✅ 登录成功！后端返回的用户信息已存储到状态管理中')
        console.log('欢迎回来:', formData.username)
        
        // 显示成功提示（短暂显示后跳转）
        successMessage.value = '登录成功！正在跳转到个人中心...'
        setTimeout(() => {
          router.push('/personal')
        }, 1500)
      } else {
        // 登录失败：显示友好的错误信息
        const errorMsg = result.message || '登录失败，请检查用户名和密码'
        console.error('❌ 登录失败:', errorMsg)
        errorMessage.value = errorMsg
        isSubmitting.value = false
      }
    } else {
      // 注册逻辑
      console.log('开始注册请求，用户名:', formData.username, '邮箱:', formData.email)
      const { data, error } = await authAPI.register({
        user_in: {
          username: formData.username,
          email: formData.email,
          password: formData.password
        },
        email_code: formData.verificationCode
      })
      
      if (!error.value && data.value) {
        // 注册成功：立即执行自动登录
        console.log('✅ 注册成功！新用户创建完成，开始自动登录...')
        successMessage.value = '注册成功！正在自动登录...'
        
        try {
          // 使用刚注册的凭据进行自动登录
          const loginResult = await authAPI.login(formData.username, formData.password)
          
          if (loginResult.success) {
            console.log('✅ 自动登录成功！欢迎新用户:', formData.username)
            successMessage.value = '注册并登录成功！正在跳转到首页...'
            
            // 跳转到个人中心
            setTimeout(() => {
              router.push('/personal')
            }, 1500)
          } else {
            // 自动登录失败，切换到登录模式让用户手动登录
            console.error('❌ 自动登录失败:', loginResult.message)
            errorMessage.value = loginResult.message || '自动登录失败，请手动登录'
            setTimeout(() => {
              isLogin.value = true
              formData.email = ''
              formData.verificationCode = ''
              errorMessage.value = ''
            }, 3000)
          }
        } catch (loginError) {
          console.error('💥 自动登录异常:', loginError)
          errorMessage.value = '自动登录过程中发生错误，请手动登录'
          setTimeout(() => {
            isLogin.value = true
            formData.email = ''
            formData.verificationCode = ''
            errorMessage.value = ''
          }, 3000)
        }
      } else {
        // 注册失败：显示友好的错误信息
        const errorMsg = error.value?.friendlyMessage || '注册失败，请检查输入信息'
        console.error('❌ 注册失败:', errorMsg)
        errorMessage.value = errorMsg
        isSubmitting.value = false
      }
    }
  } catch (error) {
    console.error('💥 网络错误或未知异常:', error)
    errorMessage.value = '无法连接到服务器，请确保后端已启动并在 http://127.0.0.1:8000 运行'
    isSubmitting.value = false
  }
}
</script>

<style lang="scss" scoped>

</style>

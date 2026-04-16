<template>
  <div class="login-page">
    <div class="login-visual">
      <div class="bg-wrapper">
        <img src="../assets/login-bg.jpg" alt="Background" class="bg-image" />
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

            <div v-if="!isLogin" class="input-group">
              <label>电子邮箱</label>
              <div class="email-input-wrapper">
                <input 
                  v-model="formData.email" 
                  type="email" 
                  placeholder="Email Address" 
                  required 
                  :disabled="codeSent"
                  @input="clearMessages"
                />
                <button 
                  type="button"
                  class="send-code-btn"
                  @click="handleSendCode"
                  :disabled="countdown > 0 || !formData.email || isSubmitting"
                >
                  {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                </button>
              </div>
            </div>

            <!-- 验证码输入框 -->
            <div v-if="!isLogin && showCodeInput" class="input-group">
              <label>验证码</label>
              <input 
                v-model="verificationCode" 
                type="text" 
                placeholder="请输入6位验证码" 
                maxlength="6"
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
const errorMessage = ref('')
const successMessage = ref('')

// 验证码相关状态
const showCodeInput = ref(false)
const verificationCode = ref('')
const codeSent = ref(false)
const countdown = ref(0)

// 响应式表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  remember: false
})

const toggleMode = () => {
  isLogin.value = !isLogin.value
  clearMessages()
}

const clearMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

/**
 * 发送邮箱验证码
 */
const handleSendCode = async () => {
  if (!formData.email) {
    errorMessage.value = '请先输入邮箱地址'
    return
  }
  
  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.email)) {
    errorMessage.value = '请输入有效的邮箱地址'
    return
  }
  
  if (countdown.value > 0) {
    return // 防止重复发送
  }

  isSubmitting.value = true
  clearMessages()

  try {
    console.log('发送验证码请求:', { email: formData.email });
    const result = await authAPI.sendVerificationCode(formData.email)
    
    if (result.success) {
      successMessage.value = '验证码已发送至您的邮箱'
      codeSent.value = true
      showCodeInput.value = true
      
      // 开始60秒倒计时
      countdown.value = 60
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    console.error('发送验证码失败:', error)
    errorMessage.value = '发送验证码失败，请稍后重试'
  } finally {
    isSubmitting.value = false
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
          router.push('/')
        }, 1500)
      } else {
        // 登录失败：显示详细的错误信息
        const errorMsg = result.message || '登录失败，请检查用户名和密码'
        console.error('❌ 登录失败:', errorMsg)
        errorMessage.value = errorMsg
        isSubmitting.value = false
      }
    } else {
      // 注册逻辑：先验证邮箱
      console.log('开始注册流程，用户名:', formData.username, '邮箱:', formData.email)
      
      // 1. 检查是否已获取验证码
      if (!codeSent.value || !verificationCode.value) {
        errorMessage.value = '请先获取并输入邮箱验证码'
        isSubmitting.value = false
        return
      }

      // 2. 验证邮箱验证码
      console.log('正在验证邮箱验证码...', { email: formData.email, code: verificationCode.value })
      
      // 确保验证码是字符串且去除空格
      const cleanCode = verificationCode.value.toString().trim();
      if (cleanCode.length !== 6) {
        errorMessage.value = '验证码必须是6位数字'
        console.error('❌ 验证码长度错误:', cleanCode.length, '原始值:', verificationCode.value)
        isSubmitting.value = false
        return
      }
      
      const verifyResult = await authAPI.verifyEmailCode({
        email: formData.email,
        code: cleanCode
      })

      if (!verifyResult.success) {
        errorMessage.value = verifyResult.message || '验证码错误，请重新输入'
        console.error('❌ 验证码验证失败:', verifyResult.message, '输入的验证码:', verificationCode.value)
        isSubmitting.value = false
        return
      }

      console.log('✅ 邮箱验证码验证成功')

      // 3. 验证码正确后，执行注册
      const result = await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      })
      
      if (result.success) {
        // 注册成功：自动切换到登录模式
        console.log('✅ 注册成功！新用户创建完成')
        successMessage.value = '注册成功！请使用新账号登录'
        setTimeout(() => {
          isLogin.value = true
          formData.email = ''
          formData.password = ''
          verificationCode.value = ''
          showCodeInput.value = false
          codeSent.value = false
          countdown.value = 0
          successMessage.value = ''
        }, 2000)
      } else {
        // 注册失败：显示详细的错误信息
        const errorMsg = result.message || '注册失败，请检查输入信息'
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
/* 错误和成功提示样式 */
.error-message,
.success-message {
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  transition: all 0.3s ease;
}

.error-message {
  background: #fef2f2;
  color: #ef4444;
  border: 1px solid #fee2e2;
}

.success-message {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #bbf7d0;
}

/* 保持你原本优秀的 CSS 样式不变 */
.login-page {
  display: flex;
  width: 100%;
  height: 100vh;
  background: #fff;
  overflow: hidden;
}

.login-visual {
  flex: 2;
  position: relative;
  .bg-wrapper {
    position: absolute;
    inset: 0;
    z-index: 1;
    .bg-image { width: 100%; height: 100%; object-fit: cover; }
    .top-shadow-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 20%, transparent 70%, rgba(0,0,0,0.6) 100%);
    }
  }
  .visual-content {
    position: relative; z-index: 2; height: 100%;
    display: flex; align-items: flex-end; padding: 80px; color: #fff;
    .brand-info {
      h1 { font-size: 3.8rem; font-weight: 800; margin-bottom: 15px; }
      .animated-bar { width: 60px; height: 5px; background: #3b82f6; margin-bottom: 25px; }
      p { letter-spacing: 5px; opacity: 0.7; font-size: 0.9rem; }
    }
  }
}

.login-form-container {
  flex: 1; min-width: 450px; background: #fff;
  display: flex; align-items: center; justify-content: center;
  padding: 60px; padding-top: 100px; position: relative; z-index: 10;
  box-shadow: -10px 0 30px rgba(0,0,0,0.03);
  .form-card { width: 100%; max-width: 360px; }
}

/* 错误提示样式 */
.error-banner {
  background: #fef2f2;
  color: #ef4444;
  padding: 12px;
  border-radius: 10px;
  font-size: 0.85rem;
  margin-bottom: 20px;
  border: 1px solid #fee2e2;
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* --- 动画 --- */
.form-stagger-enter-active { transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); }
.form-stagger-leave-active { transition: all 0.3s ease; }
.form-stagger-enter-from { opacity: 0; transform: translateY(40px); }
.form-stagger-leave-to { opacity: 0; transform: translateY(-30px); }

.text-move-enter-active, .text-move-leave-active { transition: all 0.5s ease; }
.text-move-enter-from { opacity: 0; transform: translateX(-30px); }
.text-move-leave-to { opacity: 0; transform: translateX(30px); }

/* --- 细节 --- */
.form-header {
  margin-bottom: 40px;
  h2 { font-size: 2.2rem; font-weight: 700; color: #1d1d1f; }
  p { color: #86868b; margin-top: 10px; }
}

.main-form {
  .input-group {
    margin-bottom: 20px;
    label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px; color: #1d1d1f; }
    input {
      width: 100%; padding: 14px 16px; border-radius: 12px;
      border: 1px solid #d2d2d7; background: #f5f5f7; font-size: 1rem;
      transition: all 0.3s;
      &:focus { background: #fff; border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
      &:disabled { opacity: 0.6; cursor: not-allowed; }
    }
  }

  // 邮箱输入框和按钮的布局
  .email-input-wrapper {
    display: flex;
    gap: 10px;
    
    input {
      flex: 1;
    }
    
    .send-code-btn {
      padding: 14px 16px;
      border-radius: 12px;
      border: 1px solid #d2d2d7;
      background: #f5f5f7;
      font-size: 0.9rem;
      font-weight: 500;
      color: #3b82f6;
      cursor: pointer;
      transition: all 0.3s;
      white-space: nowrap;
      
      &:hover:not(:disabled) {
        background: #e5e7eb;
        border-color: #3b82f6;
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.form-options {
  display: flex; justify-content: space-between; align-items: center; margin: 25px 0 35px; font-size: 0.9rem;
  .checkbox-label {
    display: flex; align-items: center; gap: 8px; cursor: pointer;
    .custom-check { width: 18px; height: 18px; border: 1.5px solid #d2d2d7; border-radius: 6px; }
    input:checked + .custom-check { background: #3b82f6; border-color: #3b82f6; }
    input { display: none; }
  }
  .forgot-link { color: #3b82f6; text-decoration: none; font-weight: 500; }
}

.submit-btn {
  width: 100%; padding: 16px; border-radius: 14px; border: none;
  background: #1d1d1f; color: #fff; font-size: 1.05rem; font-weight: 600;
  cursor: pointer; transition: all 0.3s;
  &:hover { background: #3b82f6; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2); }
  &:disabled { background: #d2d2d7; cursor: not-allowed; }
}

.switch-area {
  margin-top: 30px; text-align: center; font-size: 0.95rem; color: #86868b;
  .btn-toggle { background: none; border: none; color: #3b82f6; font-weight: 700; cursor: pointer; margin-left: 5px; }
}
</style>
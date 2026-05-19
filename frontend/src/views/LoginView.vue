<template>
  <div class="login-page">
    <div class="login-visual">
      <div class="bg-wrapper">
        <img src="../assets/login-bg.webp" alt="Background" class="bg-image" />
        <div class="bottom-shadow-overlay"></div>
      </div>
      <div class="visual-content">
        <transition name="text-move" mode="out-in">
          <div class="brand-info" :key="mode">
            <h1>{{ mode === 'login' ? '观测笔记' : mode === 'register' ? '加入观测' : '找回密码' }}</h1>
            <div class="animated-bar"></div>
            <p>DESIGN FOR OBSERVATION / 2026</p>
          </div>
        </transition>
      </div>
    </div>

    <div class="login-form-container">
      <div class="form-card" ref="cardRef">
        <transition name="slide-form" mode="out-in" @before-leave="beforeLeave" @after-leave="afterLeave" @enter="enter" @after-enter="afterEnter">
          <div class="inner-form-wrapper" :key="mode">
            <header class="form-header">
              <h2 v-if="mode === 'login'">登 录</h2>
              <h2 v-else-if="mode === 'register'">注 册</h2>
              <h2 v-else>忘记密码</h2>
              <p>{{ mode === 'login' ? '博主账号身份验证' : mode === 'register' ? '注册普通用户以发表评论' : '通过邮箱验证码重置密码' }}</p>
            </header>

            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
            <div v-if="successMessage" class="success-message">{{ successMessage }}</div>

            <!-- ===== 登录模式 ===== -->
            <form v-if="mode === 'login'" @submit.prevent="handleSubmit" class="main-form">
              <div class="input-group">
                <label>账号</label>
                <input v-model="formData.username" type="text" placeholder="Username" required @input="clearMessages" />
              </div>
              <div class="input-group">
                <label>密码</label>
                <input v-model="formData.password" type="password" placeholder="Password" required @input="clearMessages" />
              </div>
              <div class="form-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.remember" />
                  <span class="custom-check"></span>
                  <span>记住密码</span>
                </label>
                <a href="#" class="forgot-link" @click.prevent="mode = 'forgot'">忘记密码？</a>
              </div>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                <span>{{ isSubmitting ? '请求中...' : '立即登录' }}</span>
              </button>
            </form>

            <!-- ===== 注册模式 ===== -->
            <form v-else-if="mode === 'register'" @submit.prevent="handleSubmit" class="main-form">
              <div class="input-group">
                <label>账号</label>
                <input v-model="formData.username" type="text" placeholder="Username" required @input="clearMessages" />
              </div>
              <div class="input-group email-with-send">
                <label>电子邮箱</label>
                <div class="email-input-wrapper">
                  <input v-model="formData.email" type="email" placeholder="Email Address" required @input="clearMessages" />
                  <button type="button" class="send-code-btn" :disabled="isSendingCode || !isValidEmail(formData.email)" @click="sendVerificationCode">
                    {{ isSendingCode ? '发送中...' : '发送验证码' }}
                  </button>
                </div>
              </div>
              <div class="input-group">
                <label>邮箱验证码</label>
                <input v-model="formData.verificationCode" type="text" placeholder="请输入邮箱验证码" required @input="clearMessages" />
              </div>
              <div class="input-group">
                <label>密码</label>
                <input v-model="formData.password" type="password" placeholder="Password" required @input="clearMessages" />
              </div>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                <span>{{ isSubmitting ? '请求中...' : '提交注册' }}</span>
              </button>
            </form>

            <!-- ===== 找回密码模式 ===== -->
            <form v-else @submit.prevent="handleForgotSubmit" class="main-form">
              <div class="input-group email-with-send">
                <label>电子邮箱</label>
                <div class="email-input-wrapper">
                  <input v-model="forgotForm.email" type="email" placeholder="注册时使用的邮箱" required @input="clearMessages" />
                  <button type="button" class="send-code-btn" :disabled="forgotSending || !isValidEmail(forgotForm.email)" @click="sendForgotCode">
                    {{ forgotSending ? '发送中...' : '发送验证码' }}
                  </button>
                </div>
              </div>
              <div class="input-group">
                <label>邮箱验证码</label>
                <input v-model="forgotForm.code" type="text" placeholder="请输入邮箱验证码" required @input="clearMessages" />
              </div>
              <div class="input-group">
                <label>新密码</label>
                <input v-model="forgotForm.newPassword" type="password" placeholder="至少6个字符" required minlength="6" @input="clearMessages" />
              </div>
              <button type="submit" class="submit-btn" :disabled="forgotSubmitting">
                <span>{{ forgotSubmitting ? '重置中...' : '重置密码' }}</span>
              </button>
            </form>

            <div class="switch-area">
              <template v-if="mode === 'forgot'">
                <span>想起密码了？</span>
                <button @click="mode = 'login'" class="btn-toggle">去登录</button>
              </template>
              <template v-else>
                <span>{{ mode === 'login' ? '没有账号?' : '已有账号?' }}</span>
                <button @click="toggleMode" class="btn-toggle">{{ mode === 'login' ? '去注册' : '去登录' }}</button>
              </template>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as authService from '@/services/authService'
import { useUserStore } from '@/stores/user'

const router = useRouter(), userStore = useUserStore()
const mode = ref('login')
const isSubmitting = ref(false), isSendingCode = ref(false)
const errorMessage = ref(''), successMessage = ref(''), cardRef = ref(null)
let startHeight = 0

const beforeLeave = () => {
  if (!cardRef.value) return
  cardRef.value.style.transition = ''
  startHeight = cardRef.value.getBoundingClientRect().height
  cardRef.value.style.height = `${startHeight}px`
  cardRef.value.style.overflow = 'hidden'
}
const afterLeave = () => { if (cardRef.value) cardRef.value.style.height = 'auto' }
const enter = () => {
  if (!cardRef.value) return
  nextTick(() => {
    const targetHeight = cardRef.value.getBoundingClientRect().height
    cardRef.value.style.height = `${startHeight}px`
    cardRef.value.offsetHeight
    cardRef.value.style.transition = 'height 1.0s cubic-bezier(0.1, 0.9, 0.2, 1)'
    cardRef.value.style.height = `${targetHeight}px`
  })
}
const afterEnter = () => {
  if (!cardRef.value) return
  cardRef.value.style.transition = ''
  cardRef.value.style.height = 'auto'
  cardRef.value.style.overflow = 'auto'
}

const formData = reactive({ username: '', email: '', password: '', verificationCode: '', remember: false })
const forgotForm = reactive({ email: '', code: '', newPassword: '' })
const forgotSubmitting = ref(false), forgotSending = ref(false)

const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
const toggleMode = () => { mode.value = mode.value === 'login' ? 'register' : 'login'; clearMessages() }
const clearMessages = () => { errorMessage.value = ''; successMessage.value = '' }

const sendVerificationCode = async () => {
  if (!isValidEmail(formData.email)) return errorMessage.value = '请输入有效的邮箱地址'
  isSendingCode.value = true; errorMessage.value = ''
  try {
    const result = await authService.sendRegisterCode(formData.email)
    if (result.success) {
      successMessage.value = '验证码已发送至您的邮箱，请注意查收'
      setTimeout(() => { if (successMessage.value.includes('验证码')) successMessage.value = '' }, 3000)
    } else {
      errorMessage.value = result.message || '发送验证码失败，请稍后重试'
    }
  } catch { errorMessage.value = '网络连接异常，请检查网络后重试' }
  finally { isSendingCode.value = false }
}

const handleSubmit = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true; clearMessages()
  try {
    if (mode.value === 'login') {
      const result = await authService.login(formData.username, formData.password)
      if (result.success) {
        userStore.setAuth(result.data.accessToken, result.data.user)
        successMessage.value = '登录成功！正在跳转到个人中心...'
        setTimeout(() => router.push('/personal'), 1500)
      } else {
        errorMessage.value = result.message || '登录失败，请检查用户名和密码'
        isSubmitting.value = false
      }
    } else {
      const result = await authService.register({
        user_in: { username: formData.username, email: formData.email, password: formData.password },
        email_code: formData.verificationCode,
      })
      if (result.success) {
        successMessage.value = '注册成功！正在自动登录...'
        const loginResult = await authService.login(formData.username, formData.password)
        if (loginResult.success) {
          userStore.setAuth(loginResult.data.accessToken, loginResult.data.user)
          successMessage.value = '注册并登录成功！正在跳转到首页...'
          setTimeout(() => router.push('/personal'), 1500)
        } else {
          errorMessage.value = loginResult.message || '自动登录失败，请手动登录'
          setTimeout(() => { mode.value = 'login'; errorMessage.value = '' }, 3000)
        }
      } else {
        errorMessage.value = result.message || '注册失败，请检查输入信息'
        isSubmitting.value = false
      }
    }
  } catch {
    errorMessage.value = '无法连接到服务器，请确保后端已启动并在 http://127.0.0.1:8000 运行'
    isSubmitting.value = false
  }
}

const sendForgotCode = async () => {
  if (!isValidEmail(forgotForm.email)) return errorMessage.value = '请输入有效的邮箱地址'
  forgotSending.value = true; clearMessages()
  try {
    const result = await authService.sendForgotCode(forgotForm.email)
    if (result.success) {
      successMessage.value = '验证码已发送至您的邮箱，请注意查收'
      setTimeout(() => { if (successMessage.value.includes('验证码')) successMessage.value = '' }, 3000)
    } else {
      errorMessage.value = result.message || '发送验证码失败'
    }
  } catch { errorMessage.value = '网络连接异常' }
  finally { forgotSending.value = false }
}

const handleForgotSubmit = async () => {
  if (forgotSubmitting.value) return
  forgotSubmitting.value = true; clearMessages()
  try {
    const result = await authService.resetPassword(forgotForm.email, forgotForm.code, forgotForm.newPassword)
    if (result.success) {
      successMessage.value = '密码重置成功！请使用新密码登录'
      setTimeout(() => { mode.value = 'login'; clearMessages() }, 2000)
    } else {
      errorMessage.value = result.message || '重置密码失败'
    }
  } catch { errorMessage.value = '网络连接异常' }
  finally { forgotSubmitting.value = false }
}
</script>

<style lang="scss" scoped>
.login-page {
  display: flex; width: 100vw; height: 100vh; overflow: hidden; background-color: #050505;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.login-visual {
  flex: 1.45; position: relative; height: 100%; overflow: hidden;
  @media (max-width: 1024px) { display: none; }
  .bg-wrapper {
    width: 100%; height: 100%; position: absolute; top: 0; left: 0;
    .bg-image { width: 100%; height: 100%; object-fit: cover; }
    .bottom-shadow-overlay {
      position: absolute; bottom: 0; left: 0; width: 100%; height: 35%;
      background: linear-gradient(0deg, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.4) 50%, rgba(0, 0, 0, 0) 100%);
    }
  }
  .visual-content {
    position: relative; z-index: 2; height: 100%; display: flex; align-items: flex-end; padding: 5vw; color: #ffffff; box-sizing: border-box;
    .brand-info {
      h1 { font-size: clamp(2.2rem, 3.8vw, 4.2rem); font-weight: 900; letter-spacing: 2px; margin: 0 0 1.5vh 0; }
      .animated-bar { width: 60px; height: 4px; background: #ffffff; margin-bottom: 1.5vh; }
      p { font-size: clamp(0.75rem, 0.8vw, 0.9rem); letter-spacing: 3px; opacity: 0.6; margin: 0; }
    }
  }
}
.login-form-container {
  flex: 0.55; min-width: 340px; height: 100%; background: #ededed; display: flex; align-items: center; justify-content: center;
  padding: clamp(60px, 7vh, 90px) clamp(16px, 2.5vw, 40px) clamp(20px, 4vh, 40px) clamp(16px, 2.5vw, 40px); box-sizing: border-box;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.15); z-index: 5; overflow: hidden;
  @media (max-width: 1024px) { flex: 1; }
  .form-card {
    width: 100%; max-width: clamp(320px, 24vw, 420px); max-height: calc(100vh - clamp(80px, 10vh, 130px)); overflow-y: auto;
    background: rgba(255, 255, 255, 0.45); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.6); border-radius: 12px; padding: clamp(20px, 3vh, 34px) clamp(16px, 2vw, 32px);
    box-sizing: border-box; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04), 0 24px 48px rgba(0, 0, 0, 0.12); will-change: height;
    scrollbar-width: none; -ms-overflow-style: none;
    &::-webkit-scrollbar { display: none; width: 0 !important; height: 0 !important; background: transparent; }
  }
  .inner-form-wrapper { width: 100%; display: flex; flex-direction: column; }
  .form-header {
    margin-bottom: clamp(12px, 2.2vh, 22px); text-align: left; padding-left: 2px;
    h2 { font-size: clamp(1.35rem, 1.9vw, 1.85rem); font-weight: 800; color: #111111; margin: 0 0 6px 0; letter-spacing: 1px; }
    p { font-size: clamp(0.75rem, 0.8vw, 0.85rem); color: #555555; margin: 0; opacity: 0.8; }
  }
}
.main-form {
  .input-group {
    display: flex; flex-direction: column; margin-bottom: clamp(10px, 1.6vh, 16px);
    label { font-size: clamp(0.7rem, 0.75vw, 0.8rem); font-weight: 600; color: #222222; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; text-align: left; padding-left: 2px; }
    input[type="text"], input[type="email"], input[type="password"] {
      width: 100%; height: clamp(34px, 4vh, 42px); padding: 0 clamp(10px, 1.2vw, 16px); font-size: clamp(0.85rem, 0.9vw, 0.95rem);
      border: 1px solid rgba(0, 0, 0, 0.08); background: rgba(255, 255, 255, 0.7); border-radius: 8px; color: #111111; transition: all 0.25s ease; box-sizing: border-box; text-align: left;
      &:focus { outline: none; border-color: #0091ff; background: #ffffff; box-shadow: 0 0 0 3px rgba(0, 145, 255, 0.08); }
    }
  }
  .email-with-send .email-input-wrapper {
    display: flex; gap: clamp(6px, 1vw, 10px); input { flex: 1; }
    .send-code-btn {
      padding: 0 clamp(10px, 1.2vw, 18px); height: clamp(34px, 4vh, 42px); font-size: clamp(0.75rem, 0.8vw, 0.85rem);
      border: 1px solid #111111; background: #111111; color: #ffffff; border-radius: 8px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.2s ease; box-sizing: border-box; display: flex; align-items: center; justify-content: center;
      &:hover:not(:disabled) { background: #333333; border-color: #333333; }
      &:disabled { background: rgba(0, 0, 0, 0.05); border-color: rgba(0, 0, 0, 0.05); color: #888888; cursor: not-allowed; }
    }
  }
}
.form-options {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: clamp(12px, 2vh, 20px); font-size: clamp(0.75rem, 0.8vw, 0.85rem); padding: 0 2px;
  .checkbox-label {
    display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; color: #333333; input { display: none; }
    .custom-check {
      width: 14px; height: 14px; border: 1px solid #bbbbbb; border-radius: 4px; position: relative; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; transition: all 0.25s cubic-bezier(0.25, 1, 0.5, 1);
      &:after { content: ''; width: 7px; height: 4px; border-left: 1.5px solid #fff; border-bottom: 1.5px solid #fff; transform: rotate(-45deg) translateY(-1px); opacity: 0; transition: opacity 0.15s ease; }
    }
    input:checked + .custom-check { background: #0091ff; border-color: #0091ff; &:after { opacity: 1; } }
  }
  .forgot-link { color: #555555; text-decoration: none; cursor: pointer; transition: color 0.2s ease; &:hover { color: #0091ff; text-decoration: underline; } }
}
.submit-btn {
  width: 100%; height: clamp(36px, 4.2vh, 44px); font-size: clamp(0.85rem, 0.9vw, 1rem); background: #0091ff; color: #ffffff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; letter-spacing: 1px; display: flex; align-items: center; justify-content: center; transition: background-color 0.25s ease, box-shadow 0.25s ease;
  &:hover:not(:disabled) { background: #1a9bff; box-shadow: 0 0 12px rgba(0, 145, 255, 0.45); }
  &:disabled { background: #cccccc; color: #ffffff; cursor: not-allowed; }
}
.switch-area {
  display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: clamp(12px, 2vh, 22px); font-size: clamp(0.75rem, 0.8vw, 0.85rem); color: #555555;
  .btn-toggle {
    background: none; border: none; color: #0091ff; font-weight: 700; cursor: pointer; padding: 2px 6px; font-size: clamp(0.75rem, 0.8vw, 0.85rem); border-radius: 6px; transition: all 0.25s ease;
    &:hover { color: #1a9bff; background: rgba(0, 145, 255, 0.05); }
  }
}
.error-message, .success-message { padding: clamp(8px, 1vh, 12px) 16px; font-size: clamp(0.75rem, 0.8vw, 0.85rem); margin-bottom: 12px; text-align: left; border-radius: 8px; }
.error-message { background: #fff5f5; color: #ff4d4f; border: 1px solid rgba(255, 77, 79, 0.2); }
.success-message { background: #f6ffed; color: #52c41a; border: 1px solid rgba(82, 196, 26, 0.2); }

.text-move-enter-active, .text-move-leave-active { transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.text-move-enter-from { opacity: 0; transform: translateY(12px); }
.text-move-leave-to { opacity: 0; transform: translateY(-12px); }

.slide-form-enter-active, .slide-form-leave-active { transition: opacity 0.5s cubic-bezier(0.1, 0.9, 0.2, 1), transform 0.5s cubic-bezier(0.1, 0.9, 0.2, 1); }
.slide-form-enter-from { opacity: 0; transform: scale(0.97) translateY(8px); }
.slide-form-leave-to { opacity: 0; transform: scale(0.97) translateY(-8px); }
</style>

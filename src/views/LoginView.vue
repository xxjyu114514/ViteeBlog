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

          <form @submit.prevent="handleSubmit" class="main-form">
            <div class="input-group">
              <label>账号</label>
              <input 
                v-model="formData.username" 
                type="text" 
                placeholder="Username" 
                required 
              />
            </div>

            <div v-if="!isLogin" class="input-group">
              <label>电子邮箱</label>
              <input 
                v-model="formData.email" 
                type="email" 
                placeholder="Email Address" 
                required 
              />
            </div>

            <div class="input-group">
              <label>密码</label>
              <input 
                v-model="formData.password" 
                type="password" 
                placeholder="Password" 
                required 
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
              <span v-else>处理中...</span>
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

// 1. 初始化路由
const router = useRouter()

// 2. 响应式状态定义
const isLogin = ref(true)
const isSubmitting = ref(false)

// 3. 表单数据对象 (解决之前 Cannot read properties of undefined 的错误)
const formData = reactive({
  username: '',
  email: '',
  password: '',
  remember: false
})

// 4. 逻辑方法
const toggleMode = () => {
  isLogin.value = !isLogin.value
}

const handleSubmit = () => {
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  
  // 模拟 API 请求逻辑
  setTimeout(() => {
    isSubmitting.value = false
    console.log('提交的数据:', formData)
    
    if (isLogin.value) {
      // 登录成功跳转首页
      router.push('/')
    } else {
      // 注册成功后自动切回登录状态
      isLogin.value = true
    }
  }, 1200)
}
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  width: 100%;
  height: 100vh;
  background: #fff;
  overflow: hidden;
}

/* --- 左侧视觉区 --- */
.login-visual {
  flex: 2;
  position: relative;
  
  .bg-wrapper {
    position: absolute;
    inset: 0;
    z-index: 1;
    .bg-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .top-shadow-overlay {
      position: absolute;
      inset: 0;
      // 顶部加深，防止透明导航栏文字看不清；底部加深，承托大标题
      background: linear-gradient(to bottom, 
        rgba(0,0,0,0.4) 0%, 
        transparent 20%, 
        transparent 70%, 
        rgba(0,0,0,0.6) 100%
      );
    }
  }

  .visual-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    align-items: flex-end;
    padding: 80px;
    color: #fff;

    .brand-info {
      h1 { font-size: 3.8rem; font-weight: 800; margin-bottom: 15px; }
      .animated-bar { width: 60px; height: 5px; background: #3b82f6; margin-bottom: 25px; }
      p { letter-spacing: 5px; opacity: 0.7; font-size: 0.9rem; }
    }
  }
}

/* --- 右侧表单区 --- */
.login-form-container {
  flex: 1;
  min-width: 450px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  padding-top: 100px; // 避开顶部透明导航栏的交互区
  position: relative;
  z-index: 10;
  box-shadow: -10px 0 30px rgba(0,0,0,0.03);

  .form-card {
    width: 100%;
    max-width: 360px;
  }
}

/* --- 核心动画：解决瞬移问题 --- */
// 1. 整体表单卡片切换 (向上滑出，从下方弹入)
.form-stagger-enter-active {
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.form-stagger-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.form-stagger-enter-from {
  opacity: 0;
  transform: translateY(40px);
}
.form-stagger-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

// 2. 左侧文字横向切换
.text-move-enter-active, .text-move-leave-active {
  transition: all 0.5s ease;
}
.text-move-enter-from { opacity: 0; transform: translateX(-30px); }
.text-move-leave-to { opacity: 0; transform: translateX(30px); }

/* --- 表单细节样式 --- */
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
      width: 100%;
      padding: 14px 16px;
      border-radius: 12px;
      border: 1px solid #d2d2d7;
      background: #f5f5f7;
      font-size: 1rem;
      transition: all 0.3s;
      &:focus {
        background: #fff;
        border-color: #3b82f6;
        outline: none;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
      }
    }
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0 35px;
  font-size: 0.9rem;
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    .custom-check {
      width: 18px;
      height: 18px;
      border: 1.5px solid #d2d2d7;
      border-radius: 6px;
      transition: all 0.2s;
    }
    input:checked + .custom-check {
      background: #3b82f6;
      border-color: #3b82f6;
    }
    input { display: none; }
  }
  .forgot-link { color: #3b82f6; text-decoration: none; font-weight: 500; }
}

.submit-btn {
  width: 100%;
  padding: 16px;
  border-radius: 14px;
  border: none;
  background: #1d1d1f;
  color: #fff;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  &:hover {
    background: #3b82f6;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.2);
  }
  &:disabled { background: #d2d2d7; cursor: not-allowed; }
}

.switch-area {
  margin-top: 30px;
  text-align: center;
  font-size: 0.95rem;
  color: #86868b;
  .btn-toggle {
    background: none;
    border: none;
    color: #3b82f6;
    font-weight: 700;
    cursor: pointer;
    margin-left: 5px;
    &:hover { text-decoration: underline; }
  }
}
</style>
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
// import './styles/components.css'
import './styles/pages.css'
import "./assets/styles/_base.scss"
import "./assets/styles/_mixins.scss"
import "./assets/styles/_variables.scss"
import "./assets/styles/views.scss"

const app = createApp(App)
const pinia = createPinia()

// 关键：先安装 Pinia，再安装 Router
app.use(pinia)
app.use(router)

// 添加token过期检查和跨标签页同步
app.mount('#app')

// 在应用挂载后初始化token检查
setTimeout(() => {
  const { useUserStore } = require('@/stores/user')
  const userStore = useUserStore()
  
  // 1. 定时检查token过期状态（每分钟检查一次）
  const tokenCheckInterval = setInterval(() => {
    if (userStore.checkTokenExpiry()) {
      // token已过期并登出，可以显示通知（如果需要）
      console.log('Token已过期，用户已登出')
    }
  }, 60000)
  
  // 2. 监听localStorage变化（跨标签页同步）
  const handleStorageChange = (event) => {
    if (event.key === 'vitee_token' && event.newValue === null) {
      // 其他标签页已登出，当前标签页也应检查状态
      if (userStore.isAuthenticated) {
        userStore.logout()
        console.log('检测到其他标签页登出，当前标签页已同步登出')
      }
    }
  }
  
  window.addEventListener('storage', handleStorageChange)
  
  // 清理函数（在应用卸载时清理，但Vue应用通常不会卸载）
  // 这里主要是为了开发环境热重载时避免重复监听
  if (import.meta.hot) {
    import.meta.hot.dispose(() => {
      clearInterval(tokenCheckInterval)
      window.removeEventListener('storage', handleStorageChange)
    })
  }
}, 0)
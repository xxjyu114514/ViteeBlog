import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// ===== 暗色主题全局入口 =====
import './styles/index.scss'

// ===== 沉浸式视图样式（Home / Posts / Message） =====
import './styles/immersive.scss'

// ===== 向后兼容 =====
import './style.css'                     // 暗色 CSS 变量 + 工具类
import "./assets/styles/_mixins.scss"    // mixin工具函数
import "./assets/styles/_variables.scss" // 暗色 tokens + 别名
import "./assets/styles/views.scss"      // 登录页基础样式

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
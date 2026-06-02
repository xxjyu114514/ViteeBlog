import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// ===== 暗色主题全局入口（冷色调机能风设计系统） =====
import './styles/index.scss'

// ===== 沉浸式视图样式（Home / Posts / Message） =====
import './styles/immersive.scss'

// ===== 混合宏 + 变量别名 + 视图基础样式 =====
import "./assets/styles/_mixins.scss"
import "./assets/styles/_variables.scss"
import "./assets/styles/views.scss"

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
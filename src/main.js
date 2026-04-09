import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import './assets/main.scss' // 存放全局基础样式 

const app = createApp(App)
app.use(router) // 必须 use 才能识别 router-view
app.mount('#app')
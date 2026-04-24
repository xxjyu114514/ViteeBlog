import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
// import './styles/components.css'
// import './styles/pages.css'
import "./assets/styles/_base.scss"
import "./assets/styles/_mixins.scss"
import "./assets/styles/_variables.scss"
import "./assets/styles/views.scss"



const app = createApp(App)
const pinia = createPinia()

// 关键：先安装 Pinia，再安装 Router
app.use(pinia)
app.use(router)

app.mount('#app')
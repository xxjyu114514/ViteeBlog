<template>
  <div class="personal-center">
    <div class="glass-card">
      <header class="user-info">
        <div class="avatar-placeholder">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}</div>
        <div class="details">
          <h2>{{ userStore.userInfo?.username }}</h2>
          <span class="role-badge">{{ userStore.userInfo?.role }}</span>
        </div>
      </header>
      
      <div class="menu-section">
        <!-- 普通用户菜单 -->
        <button 
          v-if="!userStore.isAdmin"
          class="menu-item"
          @click="goToPosts"
        >
          📖 浏览文章
        </button>
        
        <!-- 管理员专属菜单 -->
        <template v-if="userStore.isAdmin">
          <button 
            class="menu-item admin-item"
            @click="goToArticleEdit"
          >
            ✍️ 新建文章
          </button>
          <button 
            class="menu-item admin-item"
            @click="goToArticleManage"
          >
            📂 文章管理
          </button>
          <button 
            class="menu-item admin-item"
            @click="goToPublishedPosts"
          >
            📰 已发布文章
          </button>
        </template>
        
        <!-- 通用菜单 -->
        <button 
          class="menu-item"
          @click="goToPosts"
        >
          🔍 浏览所有文章
        </button>
        <button 
          class="menu-item"
          @click="goToSettings"
        >
          ⚙️ 系统设置
        </button>
        
        <!-- 退出登录按钮 -->
        <button @click="handleLogout" class="menu-item logout">🚪 退出登录</button>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

// 退出登录处理函数
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 导航函数
const goToArticleEdit = () => {
  router.push('/edit-article')
}

const goToArticleManage = () => {
  router.push('/manage-articles')
}

const goToPublishedPosts = () => {
  router.push('/posts')
}

const goToPosts = () => {
  router.push('/posts')
}

const goToSettings = () => {
  // TODO: 添加系统设置页面
  alert('系统设置功能开发中...')
}
</script>

<style lang="scss" scoped>
.personal-center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);

  .glass-card {
    width: 90%;
    max-width: 500px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;

  .avatar-placeholder {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, #fff 0%, #ccc 100%);
    color: #000;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold; font-size: 1.5rem;
  }

  h2 { color: white; margin: 0; }
  .role-badge { 
    font-size: 0.7rem; 
    color: rgba(255,255,255,0.5); 
    text-transform: uppercase;
    letter-spacing: 1px;
  }
}

.menu-section {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .menu-item {
    background: rgba(255,255,255,0.05);
    border: none;
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: left;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 12px;

    &:hover { 
      background: rgba(255,255,255,0.15); 
      transform: translateX(5px); 
    }
    
    &.logout { 
      color: #ff4d4d; 
      margin-top: 20px; 
    }
    
    &.admin-item {
      background: rgba(59, 130, 246, 0.1);
      border-left: 3px solid #3b82f6;
    }
  }
}
</style>
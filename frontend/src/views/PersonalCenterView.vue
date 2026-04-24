<template>
  <div class="personal-center">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="container-grid">
      <!-- 用户信息卡片 -->
      <div class="glass-card user-info-card">
        <header class="user-info">
          <div class="avatar-placeholder">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}</div>
          <div class="details">
            <h2>{{ userStore.userInfo?.username }}</h2>
            <span class="role-badge">{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</span>
          </div>
        </header>
      </div>

      <!-- 文章创作卡片 -->
      <div class="glass-card">
        <h3 class="card-title">✍️ 文章创作</h3>
        <div class="menu-section">
          <button 
            class="menu-item"
            @click="goToArticleEdit"
          >
            新建文章
          </button>
          <button 
            class="menu-item"
            @click="goToArticleManage"
          >
            我的文章
          </button>
        </div>
      </div>

      <!-- 管理功能卡片（仅管理员可见） -->
      <div v-if="userStore.isAdmin" class="glass-card">
        <h3 class="card-title">🛠️ 管理功能</h3>
        <div class="menu-section">
          <button 
            class="menu-item admin-item"
            @click="goToAllArticlesManage"
          >
            全站文章管理
          </button>
          <button 
            class="menu-item admin-item"
            @click="goToCategoryManage"
          >
            分类管理
          </button>
          <button 
            class="menu-item admin-item"
            @click="goToTagManage"
          >
            标签管理
          </button>
        </div>
      </div>

      <!-- 通用功能卡片 -->
      <div class="glass-card">
        <h3 class="card-title">🔍 通用功能</h3>
        <div class="menu-section">
          <button 
            class="menu-item"
            @click="goToPosts"
          >
            浏览所有文章
          </button>
          <button 
            class="menu-item"
            @click="goToSettings"
          >
            系统设置
          </button>
        </div>
      </div>

      <!-- 账户操作卡片 -->
      <div class="glass-card">
        <h3 class="card-title">👤 账户操作</h3>
        <div class="menu-section">
          <button @click="handleLogout" class="menu-item logout">
            退出登录
          </button>
        </div>
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

const goToAllArticlesManage = () => {
  router.push('/manage-articles')
}

const goToCategoryManage = () => {
  router.push('/categories')
}

const goToTagManage = () => {
  router.push('/tags')
}

const goToPosts = () => {
  router.push('/posts')
}

const goToSettings = () => {
  // TODO: 添加系统设置页面
  alert('系统设置功能开发中...')
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

</script>
<template>
  <div class="personal-center">
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="container-grid">
      <div class="glass-card user-info-card">
        <header class="user-info">
          <div class="avatar-placeholder">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}</div>
          <div class="details">
            <h2>{{ userStore.userInfo?.username }}</h2>
            <span class="role-badge">{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</span>
          </div>
        </header>
      </div>

      <div class="glass-card">
        <h3 class="card-title">✍️ 文章创作</h3>
        <div class="menu-section">
          <button class="menu-item" @click="goToArticleEdit">新建文章</button>
          <button class="menu-item" @click="goToArticleManage">我的文章</button>
        </div>
      </div>

      <div v-if="userStore.isAdmin" class="glass-card">
        <h3 class="card-title">🛠️ 管理功能</h3>
        <div class="menu-section">
          <button class="menu-item admin-item" @click="goToAllArticlesManage">全站文章管理</button>
          <button class="menu-item admin-item" @click="goToCategoryManage">分类管理</button>
          <button class="menu-item admin-item" @click="goToTagManage">标签管理</button>
          <button class="menu-item admin-item" @click="goToCommentReports">举报管理</button>
          <button class="menu-item admin-item" @click="goToCommentAdmin">评论巡查</button>
        </div>
      </div>

      <div class="glass-card">
        <h3 class="card-title">🔍 通用功能</h3>
        <div class="menu-section">
          <button class="menu-item" @click="goToPosts">浏览所有文章</button>
          <button class="menu-item" @click="goToFavorites">我的收藏</button>
          <button class="menu-item" @click="goToSettings">系统设置</button>
        </div>
      </div>

      <div class="glass-card">
        <h3 class="card-title">👤 账户操作</h3>
        <div class="menu-section">
          <button @click="showChangePwd = true" class="menu-item">修改密码</button>
          <button @click="handleDeleteAccount" class="menu-item logout">注销账号</button>
          <button @click="handleLogout" class="menu-item logout">退出登录</button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showChangePwd" class="modal-overlay" @click="showChangePwd = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>修改密码</h3>
            <button class="modal-close" @click="showChangePwd = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="pwdMessage" :class="['message', pwdError ? 'error' : 'success']">{{ pwdMessage }}</div>
            <div class="form-group">
              <label>旧密码</label>
              <input v-model="pwdForm.oldPassword" type="password" class="input-field" placeholder="请输入当前密码" />
            </div>
            <div class="form-group">
              <label>新密码</label>
              <input v-model="pwdForm.newPassword" type="password" class="input-field" placeholder="至少6个字符" minlength="6" />
            </div>
            <div class="form-group">
              <label>确认新密码</label>
              <input v-model="pwdForm.confirmPassword" type="password" class="input-field" placeholder="再次输入新密码" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showChangePwd = false">取消</button>
            <button class="btn-submit" :disabled="pwdSubmitting" @click="handleChangePwd">
              {{ pwdSubmitting ? '提交中...' : '确认修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import * as authService from '@/services/authService'

const userStore = useUserStore()
const router = useRouter()

const showChangePwd = ref(false)
const pwdSubmitting = ref(false)
const pwdMessage = ref('')
const pwdError = ref(false)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const handleChangePwd = async () => {
  pwdMessage.value = ''
  if (!pwdForm.oldPassword || !pwdForm.newPassword || !pwdForm.confirmPassword) {
    pwdMessage.value = '请填写所有字段'; pwdError.value = true; return
  }
  if (pwdForm.newPassword.length < 6) {
    pwdMessage.value = '新密码至少6个字符'; pwdError.value = true; return
  }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) {
    pwdMessage.value = '两次输入的新密码不一致'; pwdError.value = true; return
  }
  pwdSubmitting.value = true
  const result = await authService.changePassword(pwdForm.oldPassword, pwdForm.newPassword)
  if (result.success) {
    pwdMessage.value = '密码修改成功！请重新登录'
    pwdError.value = false
    setTimeout(() => { showChangePwd.value = false; userStore.logout(); router.push('/login') }, 2000)
  } else {
    pwdMessage.value = result.message || '修改失败'; pwdError.value = true
  }
  pwdSubmitting.value = false
}

const handleDeleteAccount = async () => {
  if (!confirm('确定要注销账号吗？此操作不可撤销！')) return
  if (!confirm('再次确认：所有数据将被永久删除！')) return
  const r = await authService.deleteAccount()
  if (r.success) {
    alert('账号已注销')
    userStore.logout(); router.push('/login')
  } else {
    alert(r.message || '注销失败')
  }
}

const handleLogout = () => { userStore.logout(); router.push('/login') }

const goToArticleEdit = () => router.push('/edit-article')
const goToArticleManage = () => router.push('/manage-articles')
const goToAllArticlesManage = () => router.push('/manage-articles')
const goToCategoryManage = () => router.push('/categories')
const goToTagManage = () => router.push('/tags')
const goToPosts = () => router.push('/posts')
const goToFavorites = () => router.push('/favorites')
const goToSettings = () => alert('系统设置功能开发中...')
const goToCommentReports = () => router.push('/comment-reports')
const goToCommentAdmin = () => router.push('/comment-admin')
const handleBack = () => router.go(-1)
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.5); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background: white; padding: 24px; border-radius: 8px;
  width: 90%; max-width: 420px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  h3 { margin: 0; font-size: 1.2rem; }
  .modal-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: $text-secondary; }
}
.modal-body {
  .form-group { margin-bottom: 16px; label { display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 6px; color: $text-main; } }
  .input-field { width: 100%; padding: 10px 12px; border: 1px solid $border-color; border-radius: 6px; font-size: 0.95rem; box-sizing: border-box; &:focus { outline: none; border-color: $color-primary; } }
  .message { padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 12px; &.error { background: #fff5f5; color: #ff4d4f; } &.success { background: #f6ffed; color: #52c41a; } }
}
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
.btn-cancel { padding: 8px 20px; border: 1px solid $border-color; border-radius: 6px; background: white; cursor: pointer; }
.btn-submit { padding: 8px 20px; border: none; border-radius: 6px; background: $color-primary; color: white; cursor: pointer; &:disabled { opacity: 0.6; } }
</style>

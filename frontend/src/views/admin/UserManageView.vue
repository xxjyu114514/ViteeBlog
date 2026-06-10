<template>
  <div class="user-manage-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title">👑 用户管理</span>
          <span class="card-subtitle">全站用户角色管理</span>
          <div v-if="loading" class="loading-spinner"></div>
        </div>

        <div class="card-body">
          <!-- 空状态 -->
          <div v-if="!loading && users.length === 0" class="empty-state">
            <span class="empty-icon">👥</span>
            <span class="empty-text">暂无用户数据</span>
          </div>

          <!-- 用户表格 -->
          <table v-else class="user-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th class="col-user">用户</th>
                <th class="col-email">邮箱</th>
                <th class="col-role">当前角色</th>
                <th class="col-status">状态</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" :class="{ 'row-deleted': !user.isActive, 'row-self': user.id === currentUserId }">
                <td class="col-id">{{ user.id }}</td>
                <td class="col-user">
                  <div class="user-cell">
                    <span class="user-avatar">{{ user.username?.charAt(0).toUpperCase() || '?' }}</span>
                    <div class="user-info">
                      <span class="user-name">{{ user.username }}</span>
                      <span v-if="user.id === currentUserId" class="user-tag-self">我</span>
                    </div>
                  </div>
                </td>
                <td class="col-email">{{ user.email }}</td>
                <td class="col-role">
                  <span :class="['role-badge', `role-${user.role}`]">
                    {{ roleMap[user.role] || user.role }}
                  </span>
                </td>
                <td class="col-status">
                  <span :class="['status-dot', user.isActive ? 'active' : 'inactive']"></span>
                  {{ user.isActive ? '正常' : '已注销' }}
                </td>
                <td class="col-actions">
                  <!-- 不能对自己操作，不能修改超管角色 -->
                  <button
                    v-if="user.id !== currentUserId && user.role !== 'super_admin'"
                    class="btn-role"
                    :class="{ 'btn-promote': user.role === 'common', 'btn-demote': user.role === 'admin' }"
                    @click="openRoleModal(user)"
                  >
                    {{ user.role === 'common' ? '提升' : '降级' }}
                  </button>
                  <span v-else-if="user.role === 'super_admin'" class="text-protected">受保护</span>
                  <span v-else class="text-self">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 角色变更确认弹窗 -->
    <Teleport to="body">
      <div v-if="showRoleModal" class="modal-overlay" @click="showRoleModal = false">
        <div class="modal-box" @click.stop>
          <h3>确认角色变更</h3>
          <div class="modal-body">
            <div class="modal-user-info">
              <span class="modal-user-avatar">{{ targetUser?.username?.charAt(0).toUpperCase() || '?' }}</span>
              <div>
                <div class="modal-user-name">{{ targetUser?.username }}</div>
                <div class="modal-user-email">{{ targetUser?.email }}</div>
              </div>
            </div>
            <div class="change-info">
              <span class="change-label">当前角色：</span>
              <span :class="['role-badge', `role-${targetUser?.role}`]">{{ roleMap[targetUser?.role] }}</span>
            </div>
            <div class="change-info">
              <span class="change-label">变更后角色：</span>
              <span :class="['role-badge', `role-${newRole}`]">{{ roleMap[newRole] }}</span>
            </div>
            <div v-if="roleMsg" :class="['modal-msg', roleErr ? 'err' : 'ok']">{{ roleMsg }}</div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="showRoleModal = false" :disabled="roleSaving">取消</button>
            <button
              class="btn btn-primary"
              :class="{ 'btn-loading': roleSaving }"
              :disabled="roleSaving"
              @click="confirmRoleChange"
            >
              {{ roleSaving ? '处理中...' : '确认变更' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getAllUsers, updateUserRole } from '@/services/authService'

const userStore = useUserStore()
const slidIn = ref(false)
const loading = ref(true)
const users = ref([])
const currentUserId = ref(userStore.userInfo?.id)

// 角色显示映射
const roleMap = {
  super_admin: '超级管理员',
  admin: '管理员',
  common: '普通用户',
}

// 角色变更弹窗
const showRoleModal = ref(false)
const targetUser = ref(null)
const newRole = ref('')
const roleMsg = ref('')
const roleErr = ref(false)
const roleSaving = ref(false)

const openRoleModal = (user) => {
  targetUser.value = user
  newRole.value = user.role === 'common' ? 'admin' : 'common'
  roleMsg.value = ''
  roleErr.value = false
  showRoleModal.value = true
}

const confirmRoleChange = async () => {
  if (!targetUser.value || !newRole.value) return
  roleSaving.value = true
  roleMsg.value = ''
  roleErr.value = false

  const r = await updateUserRole(targetUser.value.id, newRole.value)
  if (r.success) {
    roleMsg.value = r.message || '角色变更成功！'
    roleErr.value = false
    // 更新本地用户数据
    const user = users.value.find(u => u.id === targetUser.value.id)
    if (user) user.role = newRole.value
    setTimeout(() => { showRoleModal.value = false }, 1500)
  } else {
    roleMsg.value = r.message || '操作失败'
    roleErr.value = true
  }
  roleSaving.value = false
}

const loadUsers = async () => {
  loading.value = true
  const r = await getAllUsers()
  if (r.success && r.data) {
    users.value = r.data
  }
  loading.value = false
}

onMounted(async () => {
  await loadUsers()
  requestAnimationFrame(() => { slidIn.value = true })
})
</script>

<style lang="scss">
@use 'sass:color';
@use '../_design.scss' as *;

.user-manage-page {
  position: fixed;
  inset: 0;
  z-index: 1;
  overflow: hidden;
}

.glass-wrap {
  position: absolute;
  bottom: 0;
  left: $space-lg;
  right: $space-lg;
  height: calc(100vh - 90px - 5vh);
  display: flex;
  flex-direction: column;
}

.glass-card {
  background: rgba(26, 26, 31, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid $glass-border;
  border-bottom: none;
  display: flex;
  flex-direction: column;
  height: 100%;
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.4s ease;
  overflow: hidden;
  &.slide-in { transform: translateY(0); opacity: 1; }
}

.card-header {
  display: flex;
  align-items: center;
  gap: $space-md;
  padding: $space-md $space-xl;
  border-bottom: 1px solid $glass-border;
  flex-shrink: 0;
  .card-title {
    font-family: $font-mono;
    font-size: 1rem;
    font-weight: 600;
    color: #ffd700;
  }
  .card-subtitle {
    font-size: 0.8rem;
    color: $text-tertiary;
    flex: 1;
  }
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 215, 0, 0.2);
  border-top-color: #ffd700;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.card-body {
  flex: 1;
  overflow-y: auto;
  padding: $space-xl;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $space-3xl;
  gap: $space-md;
  .empty-icon { font-size: 3rem; opacity: 0.5; }
  .empty-text { font-size: 0.9rem; color: $text-tertiary; }
}

// ===== 用户表格 =====
.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;

  th {
    text-align: left;
    padding: $space-sm $space-md;
    font-family: $font-mono;
    font-size: 0.75rem;
    color: $text-tertiary;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border-bottom: 1px solid $glass-border;
    white-space: nowrap;
  }

  td {
    padding: $space-sm $space-md;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: $text-primary;
    vertical-align: middle;
  }

  tbody tr {
    transition: background 0.15s ease;
    &:hover { background: $bg-hover; }
  }

  .row-deleted {
    opacity: 0.4;
    td { text-decoration: line-through; }
  }
  .row-self {
    background: rgba($color-primary, 0.05);
  }
}

.col-id { width: 50px; color: $text-tertiary !important; font-family: $font-mono; }
.col-email { color: $text-secondary; font-family: $font-mono; font-size: 0.8rem; }
.col-status { width: 80px; }
.col-actions { width: 100px; text-align: center; }

.user-cell {
  display: flex;
  align-items: center;
  gap: $space-sm;
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: $color-primary;
  color: $bg-base;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-name {
  font-weight: 600;
  color: $text-primary;
}

.user-tag-self {
  font-size: 0.65rem;
  padding: 1px 6px;
  background: rgba($color-primary, 0.15);
  color: $color-primary;
  border-radius: 8px;
  font-weight: 500;
}

// ===== 角色徽章 =====
.role-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  white-space: nowrap;

  &.role-super_admin {
    background: rgba(255, 215, 0, 0.15);
    color: #ffd700;
    border: 1px solid rgba(255, 215, 0, 0.2);
  }
  &.role-admin {
    background: rgba($color-primary, 0.12);
    color: $color-primary;
    border: 1px solid rgba($color-primary, 0.2);
  }
  &.role-common {
    background: rgba($text-secondary, 0.1);
    color: $text-secondary;
    border: 1px solid rgba($text-secondary, 0.15);
  }
}

// ===== 状态点 =====
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
  &.active { background: $color-success; box-shadow: 0 0 6px rgba($color-success, 0.4); }
  &.inactive { background: $color-error; }
}

// ===== 操作按钮 =====
.btn-role {
  padding: 4px 14px;
  border: 1px solid;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: $font-mono;
  letter-spacing: 0.03em;
  background: transparent;

  &.btn-promote {
    color: $color-success;
    border-color: rgba($color-success, 0.3);
    &:hover {
      background: rgba($color-success, 0.1);
      border-color: $color-success;
      box-shadow: 0 0 10px rgba($color-success, 0.2);
    }
  }
  &.btn-demote {
    color: $color-warning;
    border-color: rgba($color-warning, 0.3);
    &:hover {
      background: rgba($color-warning, 0.1);
      border-color: $color-warning;
      box-shadow: 0 0 10px rgba($color-warning, 0.2);
    }
  }
}

.text-protected {
  color: $text-tertiary;
  font-size: 0.75rem;
  font-style: italic;
}

.text-self {
  color: $text-disabled;
  font-size: 0.75rem;
}

// ===== 弹窗 =====
.modal-overlay {
  position: fixed;
  inset: 0;
  background: $bg-overlay;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-box {
  background: $bg-surface;
  border: 1px solid $glass-border;
  padding: $space-xl;
  width: 90%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: $space-md;
  h3 {
    margin: 0;
    font-family: $font-mono;
    color: #ffd700;
  }
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: $space-md;
}

.modal-user-info {
  display: flex;
  align-items: center;
  gap: $space-md;
  padding: $space-md;
  background: $bg-elevated;
  border: 1px solid $glass-border;
}

.modal-user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: $color-primary;
  color: $bg-base;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.modal-user-name {
  font-weight: 600;
  color: $text-primary;
}

.modal-user-email {
  font-size: 0.8rem;
  color: $text-tertiary;
  font-family: $font-mono;
}

.change-info {
  display: flex;
  align-items: center;
  gap: $space-sm;
  font-size: 0.85rem;
  .change-label { color: $text-secondary; }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: $space-sm;
  margin-top: $space-sm;
}

.modal-msg {
  padding: 8px 12px;
  font-size: 0.85rem;
  &.err { background: rgba($color-error, 0.1); color: $color-error; }
  &.ok { background: rgba($color-success, 0.1); color: $color-success; }
}

.btn {
  padding: 8px 16px;
  font-family: $font-mono;
  font-size: 0.8rem;
  cursor: pointer;
  border: 1px solid $glass-border;
  background: transparent;
  color: $text-primary;
  transition: all 0.2s ease;
  &:hover { border-color: $color-primary; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.btn-ghost { color: $text-secondary; &:hover { color: $text-primary; } }
.btn-primary {
  background: rgba($color-primary, 0.15);
  color: $color-primary;
  border-color: rgba($color-primary, 0.3);
  &:hover { background: rgba($color-primary, 0.25); }
}

.btn-loading {
  position: relative;
  pointer-events: none;
  opacity: 0.7;
  &::after {
    content: '';
    width: 14px;
    height: 14px;
    margin-left: 8px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    display: inline-block;
    animation: spin 0.6s linear infinite;
    vertical-align: middle;
  }
}
</style>

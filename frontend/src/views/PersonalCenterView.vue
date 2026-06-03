<template>
  <div class="pc-page">
    <div class="back-button" @click="router.push('/')">← 返回</div>

    <div class="pc-layout" :class="{ 'is-leaving': isLeaving }">
      <!-- 左侧：个人信息卡片 -->
      <div class="glass-hero-card profile-card tilt-target">
        <div class="glass-hero-card__inner profile-inner">
          <div class="profile-avatar">
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" />
            <span v-else class="avatar-letter">
              {{ userStore.userInfo?.username?.charAt(0).toUpperCase() || '?' }}
            </span>
          </div>
          <div class="profile-name">{{ userStore.userInfo?.username || '未登录' }}</div>
          <div class="profile-role">
            {{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
          </div>
          <div class="profile-stats">
            <div class="stat-item"><span class="stat-num">{{ profileStats.totalArticles }}</span><span class="stat-label">文章</span></div>
            <div class="stat-item"><span class="stat-num">{{ profileStats.followersCount }}</span><span class="stat-label">粉丝</span></div>
            <div class="stat-item"><span class="stat-num">{{ profileStats.totalFavorites }}</span><span class="stat-label">收藏</span></div>
          </div>
          <div class="profile-sub-stats">
            <div class="sub-stat-item"><span class="sub-stat-num">{{ profileStats.totalViews }}</span><span class="sub-stat-label">阅读</span></div>
            <div class="sub-stat-item"><span class="sub-stat-num">{{ profileStats.totalLikesReceived }}</span><span class="sub-stat-label">获赞</span></div>
            <div class="sub-stat-item"><span class="sub-stat-num">{{ profileStats.followingCount }}</span><span class="sub-stat-label">关注</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧：按钮组 -->
      <div class="pc-right tilt-target">
        <div class="button-panel">
          <div class="hero-row row-new">
            <div class="hero-button btn-new" data-path="/edit-article">
              <div class="hero-button__inner">
                <span class="hero-button__icon">✏️</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">新建文章</span>
                  <span class="hero-button__sub">NEW_POST</span>
                </div>
              </div>
            </div>
          </div>
          <div class="hero-row row-center row-fav">
            <div class="hero-button btn-fav" data-path="/favorites">
              <div class="hero-button__inner">
                <span class="hero-button__icon">⭐</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">已收藏文章</span>
                  <span class="hero-button__sub">FAVORITES</span>
                </div>
              </div>
            </div>
          </div>
          <div class="hero-row row-social">
            <div class="hero-button btn-social" data-path="/social">
              <div class="hero-button__inner">
                <span class="hero-button__icon">👥</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">关注列表</span>
                  <span class="hero-button__sub">SOCIAL</span>
                </div>
              </div>
            </div>
          </div>
          <div class="hero-row row-double row-bottom">
            <div class="hero-button hero-btn-half btn-manage" data-path="/manage-articles">
              <div class="hero-button__inner">
                <span class="hero-button__icon">📂</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">{{ userStore.isAdmin ? '管理中心' : '我的文章' }}</span>
                  <span class="hero-button__sub">ADMIN</span>
                </div>
              </div>
            </div>
            <div class="hero-button hero-btn-half btn-account" data-action="account">
              <div class="hero-button__inner">
                <span class="hero-button__icon">⚙️</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">账户设置</span>
                  <span class="hero-button__sub">SETTINGS</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 账户设置弹窗 -->
    <Teleport to="body">
      <div v-if="showAccountModal" class="modal-overlay" @click="showAccountModal = false">
        <div class="modal-box" @click.stop>
          <h3>账户设置</h3>
          <div class="account-actions">
            <button class="btn btn-outline btn-full" @click="triggerAvatarUpload">上传头像</button>
            <button class="btn btn-outline btn-full" @click="openEditProfile">编辑资料</button>
            <button class="btn btn-outline btn-full" @click="showChangePwd = true">修改密码</button>
            <button class="btn btn-outline btn-full" :class="{ 'btn-loading': deletingAccount }" :disabled="deletingAccount" @click="handleDeleteAccount">
              {{ deletingAccount ? '注销中...' : '注销账号' }}
            </button>
            <button class="btn btn-glass btn-full" @click="handleLogout">退出登录</button>
          </div>
          <div v-if="avatarMsg" :class="['modal-msg', avatarErr ? 'err' : 'ok']">{{ avatarMsg }}</div>
          <button class="btn btn-ghost btn-full modal-close-btn" @click="showAccountModal = false">关闭</button>
          <!-- 隐藏的文件上传输入 -->
          <input ref="avatarInputRef" type="file" accept="image/*" style="display:none" @change="handleAvatarUpload" />
        </div>
      </div>
    </Teleport>

    <!-- 编辑资料弹窗 -->
    <Teleport to="body">
      <div v-if="showEditProfile" class="modal-overlay" @click="showEditProfile = false">
        <div class="modal-box" @click.stop>
          <h3>编辑资料</h3>
          <div v-if="editProfileMsg" :class="['modal-msg', editProfileErr ? 'err' : 'ok']">{{ editProfileMsg }}</div>
          <input v-model="editProfileForm.username" class="modal-input" placeholder="昵称" maxlength="50" />
          <textarea v-model="editProfileForm.bio" class="modal-input modal-textarea" placeholder="个人简介（选填）" rows="3" maxlength="200"></textarea>
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="showEditProfile = false">取消</button>
            <button class="btn btn-primary" :class="{ 'btn-loading': editProfileSaving }" :disabled="editProfileSaving || !editProfileForm.username.trim()" @click="handleSaveProfile">
              {{ editProfileSaving ? '保存中' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 修改密码弹窗 -->
    <Teleport to="body">
      <div v-if="showChangePwd" class="modal-overlay" @click="showChangePwd = false">
        <div class="modal-box" @click.stop>
          <h3>修改密码</h3>
          <div v-if="pwdMsg" :class="['modal-msg', pwdErr ? 'err' : 'ok']">{{ pwdMsg }}</div>
          <input v-model="pwdOld" type="password" class="modal-input" placeholder="旧密码" />
          <input v-model="pwdNew" type="password" class="modal-input" placeholder="新密码 (至少6位)" />
          <input v-model="pwdConfirm" type="password" class="modal-input" placeholder="确认新密码" />
          <div class="modal-actions">
            <button class="btn btn-ghost" @click="showChangePwd = false">取消</button>
            <button class="btn btn-primary" :class="{ 'btn-loading': pwdSaving }" :disabled="pwdSaving" @click="handleChangePwd">
              {{ pwdSaving ? '修改中' : '确认' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as authService from '@/services/authService'
import { getUserProfile } from '@/services/userService'
import { uploadAvatar, updateProfile } from '@/services/authService'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_BASE = API_BASE.replace('/api/v1', '')
const router = useRouter()
const userStore = useUserStore()

const avatarUrl = ref(
  userStore.userInfo?.avatar
    ? BACKEND_BASE + userStore.userInfo.avatar
    : null
)

// 用户主页统计数据
const profileStats = ref({
  totalArticles: 0,
  followersCount: 0,
  totalFavorites: 0,
  totalViews: 0,
  totalLikesReceived: 0,
  totalComments: 0,
  followingCount: 0,
})

// ========= 3D 追踪配置 =========
const tiltConfig = {
  maxRotate: 5,           // 最大倾斜角度（度）
  perspective: 800,       // 透视深度（px）
  defaultRotateX: 0,      // 默认俯仰角（度）
  defaultRotateY: 0,      // 默认偏航角（度） 
  enableX: true,          // 是否启用 X 轴倾斜
  enableY: true,          // 是否启用 Y 轴倾斜
  resetOnLeave: true,     // 鼠标离开后是否回正
  resetDuration: 200,     // 回正动画时长（ms）
  leftDefaultY: 15,        // 左侧默认向右倾斜（正值）
  rightDefaultY: -15      // 右侧默认向左倾斜（负值）
}

// 出场动画
const isLeaving = ref(false)
const handleNav = (path) => {
  if (isLeaving.value) return
  isLeaving.value = true
  setTimeout(() => router.push(path), 350)
}

// 手动点击检测（绕过 3D transform 下浏览器的 hit-test bug）
let pcRightClickHandler = null
const initPcRightClick = () => {
  const HIT_PADDING = 8 // 容差 px，补偿 AABB 与实际透视梯形之间的偏差

  // 鼠标移动：手动控制 hover 样式
  const pcRightHoverHandler = (e) => {
    const pcRight = document.querySelector('.pc-right')
    if (!pcRight) return
    // 先清除所有 hover
    pcRight.querySelectorAll('.hero-button.hover').forEach(el => el.classList.remove('hover'))
    // 检测当前悬停的按钮
    const buttons = pcRight.querySelectorAll('.hero-button')
    for (const btn of buttons) {
      const rect = btn.getBoundingClientRect()
      if (e.clientX >= rect.left - HIT_PADDING && e.clientX <= rect.right + HIT_PADDING &&
          e.clientY >= rect.top - HIT_PADDING && e.clientY <= rect.bottom + HIT_PADDING) {
        btn.classList.add('hover')
        // 鼠标样式
        pcRight.style.cursor = 'pointer'
        return
      }
    }
    pcRight.style.cursor = ''
  }
  document.addEventListener('mousemove', pcRightHoverHandler)
  // 把引用存起来供 cleanup 使用
  if (!pcRightClickHandler) pcRightClickHandler = function() {}
  pcRightClickHandler._hover = pcRightHoverHandler

  // 点击：手动碰撞检测
  const clickHandler = (e) => {
    const pcRight = document.querySelector('.pc-right')
    if (!pcRight || !pcRight.contains(e.target)) return
    e.preventDefault()
    e.stopPropagation()

    const buttons = pcRight.querySelectorAll('.hero-button')
    for (const btn of buttons) {
      const rect = btn.getBoundingClientRect()
      // 加容差补偿透视偏差
      if (e.clientX >= rect.left - HIT_PADDING && e.clientX <= rect.right + HIT_PADDING &&
          e.clientY >= rect.top - HIT_PADDING && e.clientY <= rect.bottom + HIT_PADDING) {
        const path = btn.dataset.path
        if (path) {
          const finalPath = btn.classList.contains('btn-manage') && userStore.isAdmin
            ? '/admin-dashboard' : path
          handleNav(finalPath)
        }
        if (btn.dataset.action === 'account') {
          showAccountModal.value = true
        }
        break
      }
    }
  }
  pcRightClickHandler._click = clickHandler
  document.addEventListener('click', clickHandler, true)

  // 清理 hover 的兜底
  const clearHover = () => {
    const pcRight = document.querySelector('.pc-right')
    if (pcRight) {
      pcRight.querySelectorAll('.hero-button.hover').forEach(el => el.classList.remove('hover'))
      pcRight.style.cursor = ''
    }
  }
  pcRightClickHandler._clear = clearHover
  document.addEventListener('mouseleave', clearHover)
}

// 弹窗控制
const showAccountModal = ref(false)
const showChangePwd = ref(false)
const showEditProfile = ref(false)

// 头像上传
const avatarInputRef = ref(null)
const avatarMsg = ref('')
const avatarErr = ref(false)
const triggerAvatarUpload = () => { avatarInputRef.value?.click() }
const handleAvatarUpload = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  avatarMsg.value = ''; avatarErr.value = false
  const r = await uploadAvatar(file)
  if (r.success && r.data) {
    avatarUrl.value = BACKEND_BASE + r.data.url
    avatarMsg.value = '头像上传成功！'
    avatarErr.value = false
    // 更新store中的头像
    if (userStore.userInfo) userStore.userInfo.avatar = r.data.url
  } else {
    avatarMsg.value = r.message || '上传失败'
    avatarErr.value = true
  }
  // 清空 input 以便重复选择同一文件
  e.target.value = ''
}

// 编辑资料
const editProfileForm = ref({ username: '', bio: '' })
const editProfileMsg = ref('')
const editProfileErr = ref(false)
const editProfileSaving = ref(false)
const openEditProfile = () => {
  editProfileForm.value = {
    username: userStore.userInfo?.username || '',
    bio: userStore.userInfo?.bio || '',
  }
  editProfileMsg.value = ''
  editProfileErr.value = false
  showEditProfile.value = true
}
const handleSaveProfile = async () => {
  if (!editProfileForm.value.username.trim()) return
  editProfileSaving.value = true
  editProfileMsg.value = ''
  const r = await updateProfile({
    username: editProfileForm.value.username.trim(),
    bio: editProfileForm.value.bio.trim() || null,
  })
  if (r.success) {
    editProfileMsg.value = '资料更新成功！'
    editProfileErr.value = false
    // 更新store
    if (userStore.userInfo) {
      userStore.userInfo.username = editProfileForm.value.username.trim()
      userStore.userInfo.bio = editProfileForm.value.bio.trim()
    }
    setTimeout(() => { showEditProfile.value = false }, 1500)
  } else {
    editProfileMsg.value = r.message || '保存失败'
    editProfileErr.value = true
  }
  editProfileSaving.value = false
}

// 修改密码
const pwdOld = ref('')
const pwdNew = ref('')
const pwdConfirm = ref('')
const pwdSaving = ref(false)
const pwdMsg = ref('')
const pwdErr = ref(false)

const handleChangePwd = async () => {
  pwdMsg.value = ''
  if (!pwdOld.value || !pwdNew.value || !pwdConfirm.value) {
    pwdMsg.value = '请填写所有字段'
    pwdErr.value = true
    return
  }
  if (pwdNew.value.length < 6) {
    pwdMsg.value = '新密码至少6位'
    pwdErr.value = true
    return
  }
  if (pwdNew.value !== pwdConfirm.value) {
    pwdMsg.value = '两次密码不一致'
    pwdErr.value = true
    return
  }

  pwdSaving.value = true
  const r = await authService.changePassword(pwdOld.value, pwdNew.value)
  if (r.success) {
    pwdMsg.value = '修改成功，请重新登录'
    pwdErr.value = false
    setTimeout(() => {
      showChangePwd.value = false
      userStore.logout()
      router.push('/login')
    }, 2000)
  } else {
    pwdMsg.value = r.message || '修改失败'
    pwdErr.value = true
  }
  pwdSaving.value = false
}

// 注销账号
const deletingAccount = ref(false)
const handleDeleteAccount = async () => {
  if (!confirm('确定要注销账号吗？此操作不可撤销！')) return
  if (!confirm('再次确认：所有数据将被永久删除！')) return

  deletingAccount.value = true
  const r = await authService.deleteAccount()
  deletingAccount.value = false

  if (r.success) {
    alert('账号已注销')
    userStore.logout()
    router.push('/login')
  } else {
    alert(r.message || '注销失败')
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// ========= 优化版 3D 追踪 =========
let tiltElements = []
let rafId = null
let mouseX = 0
let mouseY = 0
let ticking = false
let resetTimer = null

const updateTilt = () => {
  if (!tiltElements.length) return

  const centerX = window.innerWidth / 2
  const centerY = window.innerHeight / 2

  let normX = (mouseX - centerX) / centerX
  let normY = (mouseY - centerY) / centerY
  normX = Math.min(Math.max(normX, -1), 1)
  normY = Math.min(Math.max(normY, -1), 1)

  const mouseRotateX = -normY * tiltConfig.maxRotate
  const mouseRotateY = normX * tiltConfig.maxRotate

  tiltElements.forEach(el => {
    const isLeft = el.classList.contains('profile-card')
    const isRight = el.classList.contains('pc-right')

    let defaultY = 0
    if (isLeft) defaultY = tiltConfig.leftDefaultY
    if (isRight) defaultY = tiltConfig.rightDefaultY

    let rotateX = tiltConfig.defaultRotateX
    let rotateY = defaultY

    if (tiltConfig.enableX) rotateX += mouseRotateX
    if (tiltConfig.enableY) rotateY += mouseRotateY

    el.style.transform = `perspective(${tiltConfig.perspective}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
  })
}

const onMouseMove = (e) => {
  mouseX = e.clientX
  mouseY = e.clientY
  if (!ticking) {
    rafId = requestAnimationFrame(() => {
      updateTilt()
      ticking = false
    })
    ticking = true
  }
}

const resetTilt = () => {
  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  ticking = false

  if (!tiltConfig.resetOnLeave) return

  if (resetTimer) cancelAnimationFrame(resetTimer)

  const elements = tiltElements.map(el => {
    const isLeft = el.classList.contains('profile-card')
    const isRight = el.classList.contains('pc-right')
    let defaultY = 0
    if (isLeft) defaultY = tiltConfig.leftDefaultY
    if (isRight) defaultY = tiltConfig.rightDefaultY

    const transform = el.style.transform
    const matchX = transform?.match(/rotateX\(([-\d.]+)deg\)/)
    const matchY = transform?.match(/rotateY\(([-\d.]+)deg\)/)
    const startX = matchX ? parseFloat(matchX[1]) : tiltConfig.defaultRotateX
    const startY = matchY ? parseFloat(matchY[1]) : defaultY

    return { el, startX, startY, targetX: tiltConfig.defaultRotateX, targetY: defaultY }
  })

  const startTime = performance.now()

  const animateReset = (now) => {
    const elapsed = now - startTime
    const progress = Math.min(1, elapsed / tiltConfig.resetDuration)
    const easeProgress = 1 - Math.pow(1 - progress, 3)

    elements.forEach(({ el, startX, startY, targetX, targetY }) => {
      const currentX = startX + (targetX - startX) * easeProgress
      const currentY = startY + (targetY - startY) * easeProgress
      el.style.transform = `perspective(${tiltConfig.perspective}px) rotateX(${currentX}deg) rotateY(${currentY}deg)`
    })

    if (progress < 1) {
      resetTimer = requestAnimationFrame(animateReset)
    } else {
      resetTimer = null
    }
  }

  resetTimer = requestAnimationFrame(animateReset)
}

const initTilt = () => {
  tiltElements = Array.from(document.querySelectorAll('.tilt-target'))
  if (!tiltElements.length) return

  // 初始化时设置默认倾斜（鼠标位于屏幕中心）
  mouseX = window.innerWidth / 2
  mouseY = window.innerHeight / 2
  updateTilt()

  window.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseleave', resetTilt)
}

const destroyTilt = () => {
  window.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseleave', resetTilt)
  if (rafId) cancelAnimationFrame(rafId)
  if (resetTimer) cancelAnimationFrame(resetTimer)
  tiltElements.forEach(el => {
    el.style.transform = ''
  })
}

// 加载用户主页统计数据
const loadProfileStats = async () => {
  const userId = userStore.userInfo?.id
  if (!userId) return
  const r = await getUserProfile(userId)
  if (r.success && r.data) {
    profileStats.value = {
      totalArticles: r.data.totalArticles ?? 0,
      followersCount: r.data.followersCount ?? 0,
      totalFavorites: r.data.totalFavorites ?? 0,
      totalViews: r.data.totalViews ?? 0,
      totalLikesReceived: r.data.totalLikesReceived ?? 0,
      totalComments: r.data.totalComments ?? 0,
      followingCount: r.data.followingCount ?? 0,
    }
    // 如果store中没有头像，从后端数据补全
    if (!avatarUrl.value && r.data.avatar) {
      avatarUrl.value = BACKEND_BASE + r.data.avatar
    }
  }
}

// 入场动画触发
onMounted(() => {
  loadProfileStats()
  requestAnimationFrame(() => {
    document.querySelector('.pc-layout')?.classList.add('entered')
  })
  initTilt()
  initPcRightClick()
})

onUnmounted(() => {
  destroyTilt()
  if (pcRightClickHandler) {
    if (pcRightClickHandler._click) document.removeEventListener('click', pcRightClickHandler._click, true)
    if (pcRightClickHandler._hover) document.removeEventListener('mousemove', pcRightClickHandler._hover)
    if (pcRightClickHandler._clear) document.removeEventListener('mouseleave', pcRightClickHandler._clear)
  }
})
</script>

<style lang="scss">
@use 'sass:color';
@use './_design.scss' as *;

.pc-page {
  background: url(../assets/personl.webp) right top / cover fixed, $bg-base;
  color: $text-primary;
  font-family: $font-sans;
  height: 100vh;
  padding: 90px $space-lg $space-lg;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  padding: 8px 16px;
  background: $glass-bg;
  backdrop-filter: blur(12px);
  color: $text-secondary;
  border: 1px solid $glass-border;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  &:hover {
    color: $text-primary;
    border-color: rgba($color-primary, 0.3);
  }
}

.pc-layout {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  height: 100%;
}

/* 左右统一的入场 + 退场动画 */
.profile-card,
.hero-row {
  transition: opacity 0.5s ease, translate 0.5s ease;
}

.profile-card {
  flex-shrink: 0;
  width: 300px;
  margin-left: 40px;
  opacity: 0;
  translate: -60px 0;
}
.hero-row {
  opacity: 0;
  translate: 60px 0;
}

.entered .profile-card,
.entered .hero-row {
  opacity: 1;
  translate: 0 0;
}

/* 退场动画 */
.pc-layout.is-leaving .profile-card,
.pc-layout.is-leaving .hero-row {
  transition: opacity 0.3s ease, translate 0.3s ease;
  opacity: 0;
}
.pc-layout.is-leaving .profile-card {
  translate: -60px 0;
}
.pc-layout.is-leaving .hero-row {
  translate: 60px 0;
}

/* 右侧按钮布局 */
.button-panel {
  display: flex;
  flex-direction: column;
  gap: $space-md;
}
.row-center {
  justify-content: center;
}
.row-double {
  display: flex;
  gap: $space-md;
  .hero-btn-half {
    width: 50%;
  }
}

/* 3D 追踪目标 */
.tilt-target {
  will-change: transform;
  transform-style: preserve-3d;
}

/* 左侧卡片内部样式 */
.profile-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $space-md;
  text-align: center;
  padding: $space-2xl $space-lg;
}

.profile-avatar {
  .avatar-img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba($color-primary, 0.3);
  }
  .avatar-letter {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: $color-primary;
    color: $bg-base;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 700;
  }
}

.profile-name {
  font-family: $font-mono;
  font-size: 1.4rem;
  font-weight: 700;
  color: $text-primary;
  letter-spacing: 0.02em;
}

.profile-role {
  font-size: 0.8rem;
  color: $color-primary;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.profile-stats {
  display: flex;
  gap: $space-lg;
  margin-top: $space-sm;
}

.profile-sub-stats {
  display: flex;
  gap: $space-md;
  margin-top: $space-xs;
  flex-wrap: wrap;
  justify-content: center;
}

.sub-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}

.sub-stat-num {
  font-family: $font-mono;
  font-size: 0.85rem;
  font-weight: 600;
  color: $text-secondary;
}

.sub-stat-label {
  font-size: 0.6rem;
  color: $text-tertiary;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-num {
  font-family: $font-mono;
  font-size: 1.2rem;
  font-weight: 700;
  color: $text-primary;
}
.stat-label {
  font-size: 0.65rem;
  color: $text-tertiary;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* 右侧容器 */
.pc-right {
  flex-shrink: 0;
  margin-right: 40px;
}

/* 按钮尺寸 */
.pc-right .button-panel .btn-new     { width: 240px; height: 120px; margin-left: 80px; }
.pc-right .button-panel .btn-fav     { width: 240px; height: 120px; margin-right: 80px; }
.pc-right .button-panel .btn-social  { width: 240px; height: 120px; margin-left: 80px; }
/* 底部两个按钮在 flex row-double 中由 .hero-btn-half 控制 50% 宽度 */
.pc-right .button-panel .btn-manage,
.pc-right .button-panel .btn-account { height: 120px; }
/* 右侧按钮禁用浏览器 hit-test，由自定义 JS 手动检测点击 */
.pc-right .hero-button { pointer-events: none; }
.pc-right .hero-button * { pointer-events: none; }
/* 手动 hover 样式（替代 :hover，因为 pointer-events: none 禁用浏览器hover） */
.pc-right .hero-button.hover {
  border-color: $glass-border-hover;
  box-shadow: $glow-brand;
}
.pc-right .hero-button.hover::after {
  opacity: 1;
}

/* 通用 loading 样式 */
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
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 弹窗样式 */
.account-actions {
  display: flex;
  flex-direction: column;
  gap: $space-md;
  padding: $space-md 0;
}
.modal-close-btn {
  margin-top: $space-sm;
}
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
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: $space-sm;
  h3 {
    margin: 0;
    font-family: $font-mono;
  }
}
.modal-input {
  padding: 10px 12px;
  background: $bg-elevated;
  border: 1px solid $glass-border;
  color: $text-primary;
  font-size: 0.95rem;
}
.modal-textarea {
  resize: vertical;
  font-family: $font-sans;
  min-height: 60px;
  box-sizing: border-box;
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
  &.err {
    background: rgba($color-error, 0.1);
    color: $color-error;
  }
  &.ok {
    background: rgba($color-success, 0.1);
    color: $color-success;
  }
}
.btn-full {
  width: 100%;
}
</style>
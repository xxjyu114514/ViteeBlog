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
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">文章</span></div>
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">粉丝</span></div>
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">收藏</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧：按钮组 -->
      <div class="pc-right tilt-target">
        <div class="button-panel">
          <div class="hero-row row-new">
            <div class="hero-button btn-new" @click="handleNav('/edit-article')">
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
            <div class="hero-button btn-fav" @click="handleNav('/favorites')">
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
            <div class="hero-button btn-social" @click="handleNav('/social')">
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
            <div class="hero-button hero-btn-half btn-manage" @click="handleNav('/manage-articles')">
              <div class="hero-button__inner">
                <span class="hero-button__icon">📂</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">{{ userStore.isAdmin ? '管理员' : '我的文章' }}</span>
                  <span class="hero-button__sub">MANAGE</span>
                </div>
              </div>
            </div>
            <div class="hero-button hero-btn-half btn-account" @click="showAccountModal = true">
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
            <button class="btn btn-outline btn-full" @click="showChangePwd = true">修改密码</button>
            <button class="btn btn-outline btn-full" :class="{ 'btn-loading': deletingAccount }" :disabled="deletingAccount" @click="handleDeleteAccount">
              {{ deletingAccount ? '注销中...' : '注销账号' }}
            </button>
            <button class="btn btn-glass btn-full" @click="handleLogout">退出登录</button>
          </div>
          <button class="btn btn-ghost btn-full modal-close-btn" @click="showAccountModal = false">关闭</button>
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

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const router = useRouter()
const userStore = useUserStore()

const avatarUrl = ref(
  userStore.userInfo?.avatar
    ? API_BASE.replace('/api/v1', '') + userStore.userInfo.avatar
    : null
)

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

// 弹窗控制
const showAccountModal = ref(false)
const showChangePwd = ref(false)

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

// 入场动画触发
onMounted(() => {
  requestAnimationFrame(() => {
    document.querySelector('.pc-layout')?.classList.add('entered')
  })
  initTilt()
})

onUnmounted(() => {
  destroyTilt()
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
.pc-right .button-panel .btn-manage  { width: 200px; height: 120px; }
.pc-right .button-panel .btn-account { width: 120px; height: 120px; }

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
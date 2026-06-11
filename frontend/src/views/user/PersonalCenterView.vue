<template>
  <div class="pc-page" :style="{ '--pc-bg': `url(${personalBg})` }">
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
          <div class="profile-role" :class="{ 'role-super': userStore.isSuperAdmin }">
            {{ userStore.roleLabel }}
            <span v-if="userStore.isSuperAdmin" class="role-badge-super">★</span>
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
            <div class="hero-button hero-btn-half btn-manage" data-path="/user-dashboard">
              <div class="hero-button__inner">
                <span class="hero-button__icon">📂</span>
                <div class="hero-button__text">
                  <span class="hero-button__label">{{ userStore.isSuperAdmin ? '超级管理' : '管理中心' }}</span>
                  <span class="hero-button__sub">{{ userStore.isSuperAdmin ? 'SUPER' : 'MANAGE' }}</span>
                </div>
              </div>
            </div>
            <div class="hero-button hero-btn-half btn-account" data-action="account">
              <div class="hero-button__inner btn-account__inner">
                <span class="hero-button__icon">⚙️</span>
                <span class="hero-button__label btn-account__label">设置</span>
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
import personalBg from '@/assets/personl.webp'
import { BACKEND_BASE_URL } from '@/api/config'

const router = useRouter()
const userStore = useUserStore()

const avatarUrl = ref(
  userStore.userInfo?.avatar
    ? BACKEND_BASE_URL + userStore.userInfo.avatar
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

/** 缓存按钮尺寸以降低 getBoundingClientRect 调用频率 */
let cachedButtonRects = []
let rectThrottleTimer = null
const RECT_REFRESH_MS = 100 // 每 100ms 刷新一次缓存

const refreshButtonRects = () => {
  const pcRight = document.querySelector('.pc-right')
  if (!pcRight) return
  const buttons = pcRight.querySelectorAll('.hero-button')
  cachedButtonRects = Array.from(buttons).map((btn) => ({
    el: btn,
    rect: btn.getBoundingClientRect(),
  }))
}

const throttledRefreshRects = () => {
  if (rectThrottleTimer) return
  rectThrottleTimer = setTimeout(() => {
    refreshButtonRects()
    rectThrottleTimer = null
  }, RECT_REFRESH_MS)
}

const initPcRightClick = () => {
  const HIT_PADDING = 8 // 容差 px，补偿 AABB 与实际透视梯形之间的偏差

  // 初始化缓存
  refreshButtonRects()
  // 窗口 resize 时重新获取尺寸
  window.addEventListener('resize', refreshButtonRects)

  // 鼠标移动：手动控制 hover 样式（使用缓存的 rect，每 100ms 刷新一次）
  const pcRightHoverHandler = (e) => {
    const pcRight = document.querySelector('.pc-right')
    if (!pcRight) return
    // 先清除所有 hover
    pcRight.querySelectorAll('.hero-button.hover').forEach(el => el.classList.remove('hover'))

    // 使用缓存的 rect 进行碰撞检测
    for (const { el, rect } of cachedButtonRects) {
      if (e.clientX >= rect.left - HIT_PADDING && e.clientX <= rect.right + HIT_PADDING &&
          e.clientY >= rect.top - HIT_PADDING && e.clientY <= rect.bottom + HIT_PADDING) {
        el.classList.add('hover')
        pcRight.style.cursor = 'pointer'
        return
      }
    }
    pcRight.style.cursor = ''
    // 鼠标静止时低频刷新缓存
    throttledRefreshRects()
  }
  document.addEventListener('mousemove', pcRightHoverHandler)
  // 把引用存起来供 cleanup 使用
  if (!pcRightClickHandler) pcRightClickHandler = function() {}
  pcRightClickHandler._hover = pcRightHoverHandler

  // 点击：手动碰撞检测（仍使用实时 rect 保证精度）
  const clickHandler = (e) => {
    const pcRight = document.querySelector('.pc-right')
    if (!pcRight || !pcRight.contains(e.target)) return
    e.preventDefault()
    e.stopPropagation()

    // 点击时刷新缓存以确保精度
    refreshButtonRects()

    for (const { el, rect } of cachedButtonRects) {
      if (e.clientX >= rect.left - HIT_PADDING && e.clientX <= rect.right + HIT_PADDING &&
          e.clientY >= rect.top - HIT_PADDING && e.clientY <= rect.bottom + HIT_PADDING) {
        const path = el.dataset.path
        if (path) {
          const finalPath = el.classList.contains('btn-manage') && userStore.isAdmin
            ? '/admin-dashboard' : path
          handleNav(finalPath)
        }
        if (el.dataset.action === 'account') {
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
    avatarUrl.value = BACKEND_BASE_URL + r.data.url
    avatarMsg.value = '头像上传成功！'
    avatarErr.value = false
    // 更新store中的头像
    if (userStore.userInfo) {
      userStore.userInfo.avatar = r.data.url
      // 同步持久化到 localStorage，防止刷新后丢失
      localStorage.setItem('vitee_user', JSON.stringify(userStore.userInfo))
    }
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
    // 后端数据覆盖本地头像（后端是权威数据源）
    if (r.data.avatar) {
      avatarUrl.value = BACKEND_BASE_URL + r.data.avatar
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
  window.removeEventListener('resize', refreshButtonRects)
  if (rectThrottleTimer) { clearTimeout(rectThrottleTimer); rectThrottleTimer = null }
})
</script>

<style lang="scss">
@use 'sass:color';
@use 'sass:map';
@use '../_design.scss' as *;

// ============================================================
//   个人主页 — 可调变量集合
//   每个按钮独立尺寸 / 图标 / 文字，改这里即可
//   注意：修改文字/图标后需同步改模板中对应内容
// ============================================================

// --- 按钮面板 ---
$panel-max-height: 80vh;        // 面板最大高度
$panel-gap:        $space-md;   // 按钮行间距

// --- 白色渐变（所有 hero-button 共用） ---
$gradient-start:   0%;
$gradient-end:     100%;
$gradient-fade-in: 65%;         // 渐变开始位置
$gradient-peak:    78%;
$gradient-stop-1:  80%;
$gradient-stop-2:  90%;
$gradient-stop-3:  100%;
$gradient-opacity: (fade:0.04, mid:0.08, strong:0.10, peak:0.15);

// ============================================================
//   每个按钮独立配置
//   w/h = 宽高, offset = 左右偏移, dir = 渐变方向
//   模板对应 data-path 见下方注释
// ============================================================

$btn-new: (
  w:      40vh,                   // 宽度
  h:      20vh,                   // 高度
  offset: 5vw,                    // 左偏移
  dir:    to right,               // 渐变方向
  icon:   '✏️',                  // 图标
  label:  '新建文章',              // 主文字
  sub:    'NEW_POST',             // 副文字
  path:   '/edit-article',        // 跳转路径
);

$btn-fav: (
  w:      38vh,
  h:      18vh,
  offset: 5vw,
  dir:    to right,
  icon:   '⭐',
  label:  '已收藏文章',
  sub:    'FAVORITES',
  path:   '/favorites',
);

$btn-social: (
  w:      36vh,
  h:      16vh,
  offset: 5vw,
  dir:    to right,
  icon:   '👥',
  label:  '关注列表',
  sub:    'SOCIAL',
  path:   '/social',
);

$btn-manage: (
  w:      33vh,                   // row-double 内 50% 宽度
  h:      17vh,
  dir:    to right,
  icon:   '📂',
  label:  '管理中心',             // 所有用户统一显示此文字
  sub:    'MANAGE',
  path:   '/user-dashboard',
);

$btn-account: (
  w:      17vh,
  h:      17vh,
  dir:    to bottom,              // 渐变朝下
  icon:   '⚙️',
  label:  '设置',
  action: 'account',              // data-action
);

// ============================================================

.pc-page {
  background: var(--pc-bg) right top / cover fixed, $bg-base;
  color: $text-primary;
  font-family: $font-sans;
  height: 100vh;
  padding: 90px $space-lg $space-lg;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
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
  gap: $panel-gap;
  max-height: $panel-max-height;
}
.row-center {
  justify-content: center;
}
.row-double {
  display: flex;
  gap: $space-md;
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
  display: flex;
  align-items: center;
  gap: 6px;
  &.role-super {
    color: #ffd700;
    font-weight: 700;
  }
}

.role-badge-super {
  font-size: 1rem;
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { text-shadow: 0 0 4px rgba(255, 215, 0, 0.5); }
  50% { text-shadow: 0 0 12px rgba(255, 215, 0, 0.9); }
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

/* 按钮尺寸（由顶部 $btn-* map 控制） */
.pc-right .button-panel .btn-new     { width: map-get($btn-new, w); height: map-get($btn-new, h); margin-left: map-get($btn-new, offset); }
.pc-right .button-panel .btn-fav     { width: map-get($btn-fav, w); height: map-get($btn-fav, h); margin-right: map-get($btn-fav, offset); }
.pc-right .button-panel .btn-social  { width: map-get($btn-social, w); height: map-get($btn-social, h); margin-left: map-get($btn-social, offset); }
.pc-right .button-panel .btn-manage  { width: map-get($btn-manage, w); height: map-get($btn-manage, h); }
.pc-right .button-panel .btn-account { width: map-get($btn-account, w); height: map-get($btn-account, h); }
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

/* ===== 账户设置按钮：方形 + 渐变朝下 + 图标在上 ===== */
.pc-right .btn-account {
  background:
    linear-gradient(map-get($btn-account, dir),
      transparent $gradient-start,
      transparent $gradient-fade-in,
      rgba(255, 255, 255, map-get($gradient-opacity, fade)) $gradient-peak,
      rgba(255, 255, 255, map-get($gradient-opacity, mid))   $gradient-stop-1,
      rgba(255, 255, 255, map-get($gradient-opacity, strong)) $gradient-stop-2,
      rgba(255, 255, 255, map-get($gradient-opacity, peak))  $gradient-stop-3
    ),
    rgba($bg-elevated, 0.82);
}

.btn-account__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-account__label {
  font-size: 0.85rem;
  font-weight: 600;
  color: $text-primary;
  font-family: $font-mono;
  letter-spacing: 0.05em;
}

/* ===== 新建文章按钮：蓝色渐变 ===== */
.pc-right .btn-new {
  background:
    linear-gradient(to top,
      rgba(29, 78, 216, 0.28) 0%,
      rgba(37, 99, 235, 0.22) 10%,
      rgba(37, 99, 235, 0.15) 25%,
      rgba(37, 99, 235, 0.06) 38%,
      transparent 43%,
      transparent 100%
    ),
    rgba($bg-elevated, 0.82);
}

</style>
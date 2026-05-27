<template>
  <div class="pc-page">
    <div class="back-button" @click="router.go(-1)">← 返回</div>

    <div class="pc-layout">
      <!-- 左：个人信息大卡片 -->
      <div class="glass-hero-card profile-card" ref="profileCardRef">
        <div class="glass-hero-card__inner">
          <div class="profile-avatar">
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" />
            <span v-else class="avatar-letter">{{ userStore.userInfo?.username?.charAt(0).toUpperCase() || '?' }}</span>
          </div>
          <div class="profile-name">{{ userStore.userInfo?.username || '未登录' }}</div>
          <div class="profile-role">{{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}</div>
          <div class="profile-stats">
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">文章</span></div>
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">粉丝</span></div>
            <div class="stat-item"><span class="stat-num">--</span><span class="stat-label">收藏</span></div>
          </div>
        </div>
      </div>

      <!-- 右：按钮组 + 内容面板 -->
      <div class="pc-right">
        <!-- 按钮面板 -->
        <transition name="btn-exit">
          <div v-if="!activePanel" class="button-panel">
            <div class="hero-row">
              <div class="hero-button" @click="openPanel('new-article')">
                <div class="hero-button__inner">
                  <span class="hero-button__icon">✏️</span>
                  <div class="hero-button__text">
                    <span class="hero-button__label">新建文章</span>
                    <span class="hero-button__sub">NEW_POST</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="hero-row row-center">
              <div class="hero-button" @click="openPanel('favorites')">
                <div class="hero-button__inner">
                  <span class="hero-button__icon">⭐</span>
                  <div class="hero-button__text">
                    <span class="hero-button__label">已收藏文章</span>
                    <span class="hero-button__sub">FAVORITES</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="hero-row">
              <div class="hero-button" @click="openPanel('social')">
                <div class="hero-button__inner">
                  <span class="hero-button__icon">👥</span>
                  <div class="hero-button__text">
                    <span class="hero-button__label">关注列表</span>
                    <span class="hero-button__sub">SOCIAL</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="hero-row row-double">
              <div class="hero-button hero-btn-half" @click="handleManageArticles">
                <div class="hero-button__inner">
                  <span class="hero-button__icon">📂</span>
                  <div class="hero-button__text">
                    <span class="hero-button__label">{{ userStore.isAdmin ? '管理员' : '我的文章' }}</span>
                    <span class="hero-button__sub">MANAGE</span>
                  </div>
                </div>
              </div>
              <div class="hero-button hero-btn-half" @click="openPanel('account')">
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
        </transition>

        <!-- 内容面板 -->
        <transition name="panel-enter">
          <div v-if="activePanel" class="content-panel">
            <div class="content-panel__header">
              <button class="panel-back" @click="closePanel">← 返回</button>
              <span class="panel-title">{{ panelTitle }}</span>
            </div>
            <div class="content-panel__body">
              <!-- 新建文章 -->
              <div v-if="activePanel === 'new-article'" class="panel-placeholder">
                <p>跳转至编辑器...</p>
                <button class="btn btn-primary" @click="router.push('/edit-article')">去新建</button>
              </div>

              <!-- 已收藏文章 -->
              <div v-else-if="activePanel === 'favorites'" class="panel-list">
                <StateWrapper :loading="favLoading" :empty="favList.length === 0" empty-text="暂无收藏文章">
                  <div v-for="item in favList" :key="item.id" class="panel-list-item" @click="router.push(`/article/${item.article?.id}`)">
                    <span class="list-title">{{ item.article?.title || '[无标题]' }}</span>
                    <span class="list-meta">{{ formatDate(item.createdAt) }}</span>
                  </div>
                </StateWrapper>
              </div>

              <!-- 关注列表 -->
              <div v-else-if="activePanel === 'social'" class="panel-list">
                <div class="panel-tabs">
                  <button :class="['tab-btn', { active: socialTab === 'following' }]" @click="socialTab = 'following'; loadSocial()">关注</button>
                  <button :class="['tab-btn', { active: socialTab === 'followers' }]" @click="socialTab = 'followers'; loadSocial()">粉丝</button>
                </div>
                <StateWrapper :loading="socialLoading" :empty="socialList.length === 0" empty-text="暂无数据">
                  <div v-for="user in socialList" :key="user.id" class="panel-list-item">
                    <span class="list-title">{{ user.username }}</span>
                  </div>
                </StateWrapper>
              </div>

              <!-- 账户设置 -->
              <div v-else-if="activePanel === 'account'" class="panel-settings">
                <button class="btn btn-outline btn-full" @click="showChangePwd = true">修改密码</button>
                <button class="btn btn-outline btn-full" @click="handleDeleteAccount">注销账号</button>
                <button class="btn btn-glass btn-full" @click="handleLogout">退出登录</button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

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
            <button class="btn btn-primary" :disabled="pwdSaving" @click="handleChangePwd">{{ pwdSaving ? '修改中...' : '确认' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as authService from '@/services/authService'
import { getMyFavorites } from '@/services/favoriteService'
import { getFollowing, getFollowers } from '@/services/socialService'
import StateWrapper from '@/components/StateWrapper.vue'
import { formatDate } from '@/utils'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const router = useRouter()
const userStore = useUserStore()

// ========== 头像 ==========
const avatarUrl = ref(userStore.userInfo?.avatar ? API_BASE.replace('/api/v1', '') + userStore.userInfo.avatar : null)

// ========== 内容面板 ==========
const activePanel = ref(null)
const panelTitle = ref('')

const panelMap = {
  'new-article': '新建文章',
  'favorites': '已收藏文章',
  'social': '关注列表',
  'account': '账户设置',
}

const openPanel = (name) => {
  activePanel.value = name; panelTitle.value = panelMap[name] || ''
  if (name === 'favorites') loadFav()
  if (name === 'social') loadSocial()
}
const closePanel = () => { activePanel.value = null }
const favList = ref([])
const favLoading = ref(false)
const loadFav = async () => {
  favLoading.value = true
  const r = await getMyFavorites({ page: 1, size: 20 })
  if (r.success) favList.value = r.data.items || []
  favLoading.value = false
}

// ========== 社交列表 ==========
const socialTab = ref('following')
const socialList = ref([])
const socialLoading = ref(false)
const loadSocial = async () => {
  const uid = userStore.userInfo?.id
  if (!uid) return
  socialLoading.value = true
  const r = socialTab.value === 'following' ? await getFollowing(uid) : await getFollowers(uid)
  if (r.success) socialList.value = r.data.items || []
  socialLoading.value = false
}

// ========== 按钮路由跳转 ==========
const handleManageArticles = () => router.push('/manage-articles')

// ========== 修改密码 ==========
const showChangePwd = ref(false)
const pwdOld = ref('')
const pwdNew = ref('')
const pwdConfirm = ref('')
const pwdSaving = ref(false)
const pwdMsg = ref('')
const pwdErr = ref(false)

const handleChangePwd = async () => {
  pwdMsg.value = ''
  if (!pwdOld.value || !pwdNew.value || !pwdConfirm.value) { pwdMsg.value = '请填写所有字段'; pwdErr.value = true; return }
  if (pwdNew.value.length < 6) { pwdMsg.value = '新密码至少6位'; pwdErr.value = true; return }
  if (pwdNew.value !== pwdConfirm.value) { pwdMsg.value = '两次密码不一致'; pwdErr.value = true; return }
  pwdSaving.value = true
  const r = await authService.changePassword(pwdOld.value, pwdNew.value)
  if (r.success) {
    pwdMsg.value = '修改成功，请重新登录'; pwdErr.value = false
    setTimeout(() => { showChangePwd.value = false; userStore.logout(); router.push('/login') }, 2000)
  } else { pwdMsg.value = r.message || '修改失败'; pwdErr.value = true }
  pwdSaving.value = false
}

// ========== 注销 ==========
const handleDeleteAccount = async () => {
  if (!confirm('确定要注销账号吗？此操作不可撤销！')) return
  if (!confirm('再次确认：所有数据将被永久删除！')) return
  const r = await authService.deleteAccount()
  if (r.success) { alert('账号已注销'); userStore.logout(); router.push('/login') }
  else { alert(r.message || '注销失败') }
}

// ========== 退出登录 ==========
const handleLogout = () => { userStore.logout(); router.push('/login') }

// ========== 伪3D鼠标追踪（仅初始按钮区域） ==========
const profileCardRef = ref(null)
const DEFAULT_ANGLE = 20
const TRACK_X = 8
const TRACK_Y = 6

const getDefaultRotateY = (el) => {
  const rect = el.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const scx = window.innerWidth / 2
  return ((scx - cx) / (window.innerWidth / 2)) * DEFAULT_ANGLE
}

let trackedElements = []
const defaultTilts = new Map()

const updateAll = (mx, my) => {
  const scx = window.innerWidth / 2
  const scy = window.innerHeight / 2
  const rx = (mx - scx) / (window.innerWidth / 2)
  const ry = (my - scy) / (window.innerHeight / 2)
  trackedElements.forEach(el => {
    const def = defaultTilts.get(el) || 0
    el.style.transform = `rotateX(${-ry * TRACK_Y}deg) rotateY(${def + rx * TRACK_X}deg)`
  })
}

const resetAll = () => {
  trackedElements.forEach(el => {
    const def = defaultTilts.get(el) || 0
    el.style.transform = `rotateX(0deg) rotateY(${def}deg)`
  })
}

const initTilt = () => {
  trackedElements = [
    ...document.querySelectorAll('.profile-card'),
    ...document.querySelectorAll('.hero-button'),
  ]
  defaultTilts.clear()
  trackedElements.forEach(el => defaultTilts.set(el, getDefaultRotateY(el)))
  resetAll()
  window.addEventListener('mousemove', (e) => updateAll(e.clientX, e.clientY))
  document.addEventListener('mouseleave', resetAll)
  window.addEventListener('resize', () => {
    trackedElements.forEach(el => defaultTilts.set(el, getDefaultRotateY(el)))
  })
}

// ========== 入场动画 ==========
onMounted(() => {
  initTilt()
  // 延迟触发入场 class
  requestAnimationFrame(() => {
    document.querySelector('.pc-layout')?.classList.add('entered')
  })
})

onUnmounted(() => {
  window.removeEventListener('mousemove', updateAll)
  document.removeEventListener('mouseleave', resetAll)
})
</script>

<style lang="scss">
// 引入冷色调设计系统
@use 'sass:color';
@use '@/assets/styles/variables' as *;
@use './test_scss/tokens' as t;
@use './test_scss/glass';
@use './test_scss/buttons';
@use './test_scss/components';

.pc-page {
  background: t.$bg-base;
  color: t.$text-primary;
  font-family: t.$font-sans;
  min-height: 100vh;
  padding: t.$space-lg;
  position: relative;
  overflow-x: hidden;
}

.back-button {
  position: fixed; top: 16px; left: 16px; z-index: 100;
  padding: 8px 16px; background: t.$glass-bg; backdrop-filter: blur(12px);
  color: t.$text-secondary; border: 1px solid t.$glass-border;
  cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
  &:hover { color: t.$text-primary; border-color: rgba(t.$color-primary, 0.3); }
}

// ========== 双栏布局 ==========
.pc-layout {
  display: flex;
  gap: t.$space-xl;
  align-items: flex-start;
  justify-content: center;
  max-width: 1200px;
  margin: 60px auto 0;
  // 入场初始状态
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;

  &.entered {
    opacity: 1;
    transform: translateY(0);
  }
}

// ========== 左：个人信息卡片 ==========
.profile-card {
  flex-shrink: 0;
  transition: transform 0.12s ease-out;

  .glass-hero-card__inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: t.$space-md;
    text-align: center;
    padding: t.$space-2xl t.$space-lg;
  }
}

.profile-avatar {
  .avatar-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(t.$color-primary, 0.3); }
  .avatar-letter { width: 80px; height: 80px; border-radius: 50%; background: t.$color-primary; color: t.$bg-base; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; }
}

.profile-name { font-family: t.$font-mono; font-size: 1.4rem; font-weight: 700; color: t.$text-primary; letter-spacing: 0.02em; }
.profile-role { font-size: 0.8rem; color: t.$color-primary; text-transform: uppercase; letter-spacing: 0.08em; }

.profile-stats { display: flex; gap: t.$space-lg; margin-top: t.$space-sm; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-num { font-family: t.$font-mono; font-size: 1.2rem; font-weight: 700; color: t.$text-primary; }
.stat-label { font-size: 0.65rem; color: t.$text-tertiary; text-transform: uppercase; letter-spacing: 0.06em; }

// ========== 右：按钮 + 内容面板 ==========
.pc-right {
  flex: 1;
  max-width: 560px;
  position: relative;
  perspective: 800px;
}

.button-panel {
  display: flex;
  flex-direction: column;
  gap: t.$space-md;

  .hero-row { display: flex; justify-content: flex-start; }
  .row-center { justify-content: center; }
  .row-double { display: flex; gap: t.$space-md; .hero-btn-half { width: 50%; } }
}

// 入口动画：按钮从右向左 + 透明度
.hero-button {
  opacity: 0;
  transform: translateX(60px);
  transition: opacity 0.5s ease, transform 0.5s ease, transform 0.12s ease-out;

  .entered & {
    opacity: 1;
    transform: translateX(0);
  }

  // 错开延时
  .hero-row:nth-child(1) & { transition-delay: 0.1s; }
  .hero-row:nth-child(2) & { transition-delay: 0.2s; }
  .hero-row:nth-child(3) & { transition-delay: 0.3s; }
  .hero-row:nth-child(4) & { transition-delay: 0.4s; }
}

// 按钮消失动画（点击后）
.btn-exit-leave-active { transition: all 0.4s ease; }
.btn-exit-leave-to { opacity: 0; transform: translateX(80px); }

// ========== 内容面板（滑入） ==========
.content-panel {
  position: absolute;
  top: 0; left: 0; right: 0;
  background: t.$bg-surface;
  border: 1px solid t.$glass-border;
  min-height: 520px;
  display: flex;
  flex-direction: column;
  // 禁用3D追踪
  transform: none !important;
}

.panel-enter-enter-active { transition: all 0.4s ease; }
.panel-enter-enter-from { opacity: 0; transform: translateX(60px); }
.panel-enter-leave-active { transition: all 0.3s ease; }
.panel-enter-leave-to { opacity: 0; transform: translateX(60px); }

.content-panel__header {
  display: flex; align-items: center; gap: t.$space-md;
  padding: t.$space-md t.$space-lg;
  border-bottom: 1px solid t.$glass-border;

  .panel-back { background: none; border: none; color: t.$text-secondary; cursor: pointer; font-size: 0.9rem; padding: 0; &:hover { color: t.$text-primary; } }
  .panel-title { font-family: t.$font-mono; font-size: 1rem; font-weight: 600; color: t.$text-primary; }
}

.content-panel__body { flex: 1; padding: t.$space-lg; overflow-y: auto; }

.panel-placeholder { text-align: center; padding: t.$space-2xl 0; color: t.$text-secondary; }
.panel-list { display: flex; flex-direction: column; gap: 4px; }
.panel-list-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: t.$space-sm t.$space-md;
  cursor: pointer; transition: background 0.15s;
  &:hover { background: t.$bg-hover; }
  .list-title { color: t.$text-primary; font-size: 0.95rem; }
  .list-meta { color: t.$text-tertiary; font-size: 0.8rem; }
}

.panel-tabs { display: flex; gap: 0; margin-bottom: t.$space-md; border-bottom: 1px solid t.$glass-border; }
.tab-btn { padding: t.$space-xs t.$space-lg; background: none; border: none; color: t.$text-secondary; cursor: pointer; font-size: 0.9rem; border-bottom: 2px solid transparent; margin-bottom: -1px; &.active { color: t.$color-primary; border-bottom-color: t.$color-primary; } }

.panel-settings { display: flex; flex-direction: column; gap: t.$space-md; padding: t.$space-lg 0; }
.btn-full { width: 100%; }

// ========== 弹窗样式 ==========
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: t.$bg-overlay; display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-box { background: t.$bg-surface; border: 1px solid t.$glass-border; padding: t.$space-xl; width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: t.$space-sm; h3 { margin: 0; font-family: t.$font-mono; } }
.modal-input { padding: 10px 12px; background: t.$bg-elevated; border: 1px solid t.$glass-border; color: t.$text-primary; font-size: 0.95rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: t.$space-sm; margin-top: t.$space-sm; }
.modal-msg { padding: 8px 12px; font-size: 0.85rem; &.err { background: rgba(t.$color-error, 0.1); color: t.$color-error; } &.ok { background: rgba(t.$color-success, 0.1); color: t.$color-success; } }
</style>

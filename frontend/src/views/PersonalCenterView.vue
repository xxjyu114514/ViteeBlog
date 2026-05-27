<template>
  <div class="pc-page">
    <div class="back-button" @click="router.push('/')">← 返回</div>

    <div class="pc-layout">
      <!-- 左：个人信息卡片 -->
      <div class="glass-hero-card profile-card">
        <div class="glass-hero-card__inner profile-inner">
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

      <!-- 右：按钮组（退出动画 → 跳转路由） -->
      <div class="pc-right" :class="{ 'is-leaving': isLeaving }">
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

    <!-- 账户弹窗 + 修改密码弹窗（保持不变） -->
    <Teleport to="body">
      <div v-if="showAccountModal" class="modal-overlay" @click="showAccountModal = false">
        <div class="modal-box" @click.stop>
          <h3>账户设置</h3>
          <div class="account-actions">
            <button class="btn btn-outline btn-full" @click="showChangePwd = true">修改密码</button>
            <button class="btn btn-outline btn-full" @click="handleDeleteAccount">注销账号</button>
            <button class="btn btn-glass btn-full" @click="handleLogout">退出登录</button>
          </div>
          <button class="btn btn-ghost btn-full modal-close-btn" @click="showAccountModal = false">关闭</button>
        </div>
      </div>
    </Teleport>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as authService from '@/services/authService'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const router = useRouter()
const userStore = useUserStore()
const avatarUrl = ref(userStore.userInfo?.avatar ? API_BASE.replace('/api/v1', '') + userStore.userInfo.avatar : null)

// 退出动画 → 跳转路由
const isLeaving = ref(false)
const handleNav = (path) => {
  if (isLeaving.value) return
  isLeaving.value = true
  setTimeout(() => { router.push(path) }, 350)
}

// 账户弹窗
const showAccountModal = ref(false)
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
const handleDeleteAccount = async () => {
  if (!confirm('确定要注销账号吗？此操作不可撤销！')) return
  if (!confirm('再次确认：所有数据将被永久删除！')) return
  const r = await authService.deleteAccount()
  if (r.success) { alert('账号已注销'); userStore.logout(); router.push('/login') }
  else { alert(r.message || '注销失败') }
}
const handleLogout = () => { userStore.logout(); router.push('/login') }

// 3D 鼠标追踪
const DEFAULT_ANGLE = 50; const TRACK_X = 10; const TRACK_Y = 0
let allElements = []; const individualDefs = new Map(); let groupDef = 0
function getCenterX(el) { const r = el.getBoundingClientRect(); return r.left + r.width / 2 }
function calcDef(cx) { const scx = window.innerWidth / 2; return ((scx - cx) / (window.innerWidth / 2)) * DEFAULT_ANGLE }
function refreshGroupDef() { const g = document.querySelector('.pc-right'); if (g) groupDef = calcDef(getCenterX(g)) }
function updateAll(mx, my) {
  const scx = window.innerWidth / 2; const scy = window.innerHeight / 2
  const rx = (mx - scx) / (window.innerWidth / 2); const ry = (my - scy) / (window.innerHeight / 2)
  allElements.forEach(el => {
    const def = el.classList.contains('pc-right') ? groupDef : (individualDefs.get(el) || 0)
    el.style.transform = `rotateX(${-ry * TRACK_Y}deg) rotateY(${def + rx * TRACK_X}deg)`
  })
}
function resetAll() { allElements.forEach(el => { const def = el.classList.contains('pc-right') ? groupDef : (individualDefs.get(el) || 0); el.style.transform = `rotateX(0deg) rotateY(${def}deg)` }) }
function onGlobalMove(e) { updateAll(e.clientX, e.clientY) }
function onGlobalLeave() { resetAll() }
function onResize() { refreshGroupDef(); document.querySelectorAll('.glass-hero-card').forEach(el => individualDefs.set(el, calcDef(getCenterX(el)))) }
function initTilt() {
  allElements = [...document.querySelectorAll('.glass-hero-card'), document.querySelector('.pc-right')].filter(Boolean)
  individualDefs.clear(); document.querySelectorAll('.glass-hero-card').forEach(el => individualDefs.set(el, calcDef(getCenterX(el))))
  refreshGroupDef(); resetAll()
  requestAnimationFrame(() => document.querySelector('.pc-layout')?.classList.add('entered'))
  window.addEventListener('mousemove', onGlobalMove); document.addEventListener('mouseleave', onGlobalLeave)
}
onMounted(() => { initTilt(); window.addEventListener('resize', onResize) })
onUnmounted(() => { window.removeEventListener('mousemove', onGlobalMove); window.removeEventListener('mouseleave', onGlobalLeave); window.removeEventListener('resize', onResize) })
</script>

<style lang="scss">
@use 'sass:color';
@import './test_scss.scss';

.pc-page {
  background: url(../assets/personl.webp) right top / cover fixed, $bg-base;
  color: $text-primary; font-family: $font-sans;
  height: 100vh; padding: 90px $space-lg $space-lg;
  position: relative; overflow: hidden; box-sizing: border-box;
}
.back-button {
  position: fixed; top: 16px; left: 16px; z-index: 100;
  padding: 8px 16px; background: $glass-bg; backdrop-filter: blur(12px);
  color: $text-secondary; border: 1px solid $glass-border;
  cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s;
  &:hover { color: $text-primary; border-color: rgba($color-primary, 0.3); }
}
.pc-layout {
  display: flex; align-items: flex-start; justify-content: space-between;
  height: 100%; perspective: 800px;
}
.profile-card { flex-shrink: 0; width: 300px; transition: width 0.4s ease, opacity 0.5s ease, translate 0.5s ease; margin-left: 40px; }
.profile-inner { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: $space-md; text-align: center; padding: $space-2xl $space-lg; }
.profile-avatar { .avatar-img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid rgba($color-primary, 0.3); } .avatar-letter { width: 80px; height: 80px; border-radius: 50%; background: $color-primary; color: $bg-base; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700; } }
.profile-name { font-family: $font-mono; font-size: 1.4rem; font-weight: 700; color: $text-primary; letter-spacing: 0.02em; }
.profile-role { font-size: 0.8rem; color: $color-primary; text-transform: uppercase; letter-spacing: 0.08em; }
.profile-stats { display: flex; gap: $space-lg; margin-top: $space-sm; }
.stat-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-num { font-family: $font-mono; font-size: 1.2rem; font-weight: 700; color: $text-primary; }
.stat-label { font-size: 0.65rem; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.06em; }
.pc-right { flex-shrink: 0; transform-style: preserve-3d; margin-right: 40px; }
.button-panel { display: flex; flex-direction: column; gap: $space-md; transform-style: preserve-3d; .hero-row { display: flex; justify-content: flex-start; transform-style: preserve-3d; } .row-center { justify-content: center; } .row-double { display: flex; gap: $space-md; .hero-btn-half { width: 50%; } } }

// 入场/出场
.profile-card { opacity: 0; translate: -40px 0; }
.hero-row { opacity: 0; translate: 60px 0; transition: opacity 0.5s ease, translate 0.5s ease; }
.entered .profile-card { opacity: 1; translate: 0 0; transition: opacity 0.5s ease, translate 0.5s ease; }
.entered .hero-row { opacity: 1; translate: 0 0; }
.entered .hero-row:nth-child(1) { transition-delay: 0.15s; }
.entered .hero-row:nth-child(2) { transition-delay: 0.25s; }
.entered .hero-row:nth-child(3) { transition-delay: 0.35s; }
.entered .hero-row:nth-child(4) { transition-delay: 0.45s; }
.pc-right.is-leaving .hero-row { opacity: 0; translate: 80px 0; transition: opacity 0.3s ease, translate 0.3s ease; }
.pc-right.is-leaving .hero-row:nth-child(1) { transition-delay: 0s; }
.pc-right.is-leaving .hero-row:nth-child(2) { transition-delay: 0.05s; }
.pc-right.is-leaving .hero-row:nth-child(3) { transition-delay: 0.1s; }
.pc-right.is-leaving .hero-row:nth-child(4) { transition-delay: 0.15s; }

// 弹窗
.account-actions { display: flex; flex-direction: column; gap: $space-md; padding: $space-md 0; }
.modal-close-btn { margin-top: $space-sm; }
.modal-overlay { position: fixed; inset: 0; background: $bg-overlay; display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-box { background: $bg-surface; border: 1px solid $glass-border; padding: $space-xl; width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: $space-sm; h3 { margin: 0; font-family: $font-mono; } }
.modal-input { padding: 10px 12px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-primary; font-size: 0.95rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: $space-sm; margin-top: $space-sm; }
.modal-msg { padding: 8px 12px; font-size: 0.85rem; &.err { background: rgba($color-error, 0.1); color: $color-error; } &.ok { background: rgba($color-success, 0.1); color: $color-success; } }
.btn-full { width: 100%; }

// 按钮尺寸
.pc-right .button-panel .btn-new     { width: 240px; height: 120px; margin-left: 80px; }
.pc-right .button-panel .btn-fav     { width: 240px; height: 120px; margin-right: 80px; }
.pc-right .button-panel .btn-social  { width: 240px; height: 120px; margin-left: 80px; }
.pc-right .button-panel .btn-manage  { width: 200px; height: 120px; }
.pc-right .button-panel .btn-account { width: 120px; height: 120px; }
</style>

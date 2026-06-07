<template>
  <div class="social-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title">社交关系</span>
        </div>
        <div class="card-body">
          <div class="tab-bar">
            <button :class="['tab-btn', { active: tab === 'following' }]" @click="tab = 'following'; fetchList()">关注 {{ followingTotal }}</button>
            <button :class="['tab-btn', { active: tab === 'followers' }]" @click="tab = 'followers'; fetchList()">粉丝 {{ followersTotal }}</button>
          </div>
          <StateWrapper :loading="loading" :empty="items.length === 0" :empty-text="tab === 'following' ? '还没有关注任何人' : '还没有粉丝'" @retry="fetchList">
            <div class="user-list">
              <div v-for="user in items" :key="user.id" class="user-item" @click="router.push(`/users/${user.id}`)">
                <div class="user-avatar">
                  <img v-if="user.avatar" :src="getAvatarUrl(user.avatar)" class="avatar-img" />
                  <span v-else class="avatar-letter">{{ user.username.charAt(0).toUpperCase() }}</span>
                </div>
                <span class="user-name">{{ user.username }}</span>
              </div>
            </div>
          </StateWrapper>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getFollowing, getFollowers } from '@/services/socialService'
import StateWrapper from '@/components/StateWrapper.vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const router = useRouter()
const userStore = useUserStore()

const tab = ref('following')
const items = ref([])
const loading = ref(true)
const followingTotal = ref(0)
const followersTotal = ref(0)
const slidIn = ref(false)

const getAvatarUrl = (path) => path ? API_BASE.replace('/api/v1', '') + path : ''
const goBack = () => router.push('/personal')

const fetchList = async () => {
  const userId = userStore.userInfo?.id
  if (!userId) return
  loading.value = true
  if (tab.value === 'following') {
    const r = await getFollowing(userId)
    if (r.success) { items.value = r.data.items || []; followingTotal.value = r.data.total || 0 }
  } else {
    const r = await getFollowers(userId)
    if (r.success) { items.value = r.data.items || []; followersTotal.value = r.data.total || 0 }
  }
  loading.value = false
}

onMounted(() => { fetchList(); requestAnimationFrame(() => { slidIn.value = true }) })
</script>

<style lang="scss">
@use 'sass:color';
@use '../_design.scss' as *;

.social-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

.glass-wrap {
  position: absolute; bottom: 0; left: $space-lg; right: $space-lg;
  height: calc(100vh - 90px - 5vh); display: flex; flex-direction: column;
}

.glass-card {
  background: rgba(26, 26, 31, 0.92);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid $glass-border; border-bottom: none;
  display: flex; flex-direction: column; height: 100%;
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.4s ease;
  overflow: hidden;
  &.slide-in { transform: translateY(0); opacity: 1; }
}

.card-header {
  display: flex; align-items: center; gap: $space-md;
  padding: $space-md $space-xl;
  border-bottom: 1px solid $glass-border; flex-shrink: 0;
  // .btn-back 5df2572851685c40 views.scss 4e2d5b9a4e49
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.tab-bar { display: flex; gap: 0; margin-bottom: $space-lg; border-bottom: 1px solid $glass-border; }
.tab-btn {
  padding: $space-xs $space-lg; font-size: 0.9rem; cursor: pointer;
  border: none; background: none; color: $text-secondary; border-bottom: 2px solid transparent; margin-bottom: -1px;
  &.active { color: $color-primary; border-bottom-color: $color-primary; }
}

.user-list { display: flex; flex-direction: column; gap: 4px; }
.user-item {
  display: flex; align-items: center; gap: $space-sm; padding: $space-sm $space-md;
  cursor: pointer; transition: background 0.15s;
  &:hover { background: $bg-hover; }
}
.user-avatar { flex-shrink: 0; }
.avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }
.avatar-letter { width: 36px; height: 36px; border-radius: 50%; background: $color-primary; color: $bg-base; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.9rem; }
.user-name { font-weight: 500; color: $text-primary; }
</style>

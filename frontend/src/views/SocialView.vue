<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="back-button" @click="router.go(-1)">← 返回</div>
    <div class="container-narrow mt-30">
      <h1 class="title-large mb-30">社交关系</h1>

      <div class="tab-bar">
        <button :class="['tab-btn', { active: tab === 'following' }]" @click="tab = 'following'; fetchList()">关注 {{ followingTotal }}</button>
        <button :class="['tab-btn', { active: tab === 'followers' }]" @click="tab = 'followers'; fetchList()">粉丝 {{ followersTotal }}</button>
      </div>

      <StateWrapper :loading="loading" :empty="items.length === 0" :empty-text="tab === 'following' ? '还没有关注任何人' : '还没有粉丝'" @retry="fetchList">
        <div class="user-list">
          <div v-for="user in items" :key="user.id" class="user-item">
            <div class="user-avatar">
              <img v-if="user.avatar" :src="getAvatarUrl(user.avatar)" class="avatar-img" />
              <span v-else class="avatar-letter">{{ user.username.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="user-info">
              <span class="user-name">{{ user.username }}</span>
            </div>
          </div>
        </div>
      </StateWrapper>
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

const getAvatarUrl = (path) => path ? API_BASE.replace('/api/v1', '') + path : ''

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

onMounted(() => fetchList())
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.tab-bar { display: flex; gap: 0; margin-bottom: 24px; border-bottom: 2px solid $border-color; }
.tab-btn {
  padding: 10px 24px; font-size: 0.95rem; font-weight: 500; cursor: pointer;
  border: none; background: none; color: $text-secondary; border-bottom: 2px solid transparent; margin-bottom: -2px;
  &.active { color: $color-primary; border-bottom-color: $color-primary; }
}

.user-list { display: flex; flex-direction: column; gap: 8px; }
.user-item {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  border-radius: 8px; cursor: pointer; transition: background 0.15s;
  &:hover { background: $bg-smoke; }
}
.user-avatar { flex-shrink: 0; }
.avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
.avatar-letter { width: 40px; height: 40px; border-radius: 50%; background: $color-primary; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 1rem; }
.user-name { font-weight: 500; color: $text-main; }
</style>

<template>
  <div class="user-profile-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title" v-if="profile">{{ profile.username }} 的主页</span>
          <span class="card-title" v-else>用户主页</span>
        </div>

        <div class="card-body" v-if="loading">
          <div class="state-msg"><div class="spinner"></div><p>加载中...</p></div>
        </div>

        <div class="card-body" v-else-if="error">
          <div class="state-msg"><p>{{ error }}</p><button class="btn btn-primary btn-sm mt-20" @click="loadProfile">重试</button></div>
        </div>

        <template v-else-if="profile">
          <!-- 用户信息区 -->
          <div class="profile-section">
            <div class="profile-header-info">
              <div class="profile-avatar">
                <img v-if="profile.avatar" :src="getFileUrl(profile.avatar)" class="avatar-img" />
                <span v-else class="avatar-letter">{{ profile.username?.charAt(0).toUpperCase() || '?' }}</span>
              </div>
              <div class="profile-detail">
                <h2 class="profile-username">{{ profile.username }}</h2>
                <span class="profile-role">{{ profile.role === 'admin' ? '管理员' : '普通用户' }}</span>
                <p v-if="profile.bio" class="profile-bio">{{ profile.bio }}</p>
                <button
                  v-if="canFollow"
                  class="btn-follow"
                  :class="{ following: isFollowing }"
                  :disabled="followLoading"
                  @click="toggleFollow"
                >
                  {{ followLoading ? '...' : (isFollowing ? '✓ 已关注' : '+ 关注') }}
                </button>
              </div>
            </div>

            <div class="profile-stats-row">
              <div class="stat-cell"><span class="stat-val">{{ profile.totalArticles }}</span><span class="stat-lbl">文章</span></div>
              <div class="stat-cell"><span class="stat-val">{{ profile.followersCount }}</span><span class="stat-lbl">粉丝</span></div>
              <div class="stat-cell"><span class="stat-val">{{ profile.totalLikesReceived }}</span><span class="stat-lbl">获赞</span></div>
              <div class="stat-cell"><span class="stat-val">{{ profile.totalViews }}</span><span class="stat-lbl">阅读</span></div>
              <div class="stat-cell"><span class="stat-val">{{ profile.totalFavorites }}</span><span class="stat-lbl">收藏</span></div>
            </div>
          </div>

          <!-- 文章列表 -->
          <div class="articles-section">
            <h3 class="section-title">TA 的文章</h3>
            <div v-if="articlesLoading" class="state-msg"><div class="spinner"></div><p>加载文章列表...</p></div>
            <div v-else-if="articles.length === 0" class="state-msg"><p>暂无公开文章</p></div>
            <div v-else class="article-list">
              <div
                v-for="article in articles"
                :key="article.id"
                class="article-row"
                @click="router.push(`/article/${article.id}`)"
              >
                <div class="article-row-title">{{ article.title || '[无标题]' }}</div>
                <div class="article-row-meta">
                  <span>{{ formatDate(article.publishedAt || article.createdAt) }}</span>
                  <span>阅读 {{ article.viewCount || 0 }}</span>
                </div>
              </div>
              <div v-if="articlesTotalPages > 1" class="pagination">
                <button class="page-btn" :disabled="articlesPage <= 1" @click="loadArticles(articlesPage - 1)">上一页</button>
                <span class="page-info">{{ articlesPage }} / {{ articlesTotalPages }}</span>
                <button class="page-btn" :disabled="articlesPage >= articlesTotalPages" @click="loadArticles(articlesPage + 1)">下一页</button>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserProfile, getUserArticles } from '@/services/userService'
import { followUser, unfollowUser } from '@/services/socialService'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const BACKEND_BASE = API_BASE.replace('/api/v1', '')
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const profile = ref(null)
const loading = ref(true)
const error = ref(null)
const slidIn = ref(false)
const isFollowing = ref(false)
const followLoading = ref(false)

const articles = ref([])
const articlesLoading = ref(false)
const articlesPage = ref(1)
const articlesTotalPages = ref(0)
const pageSize = 10

const canFollow = computed(() =>
  userStore.isAuthenticated &&
  profile.value &&
  profile.value.id !== userStore.userInfo?.id
)

const getFileUrl = (path) => path ? BACKEND_BASE + path : ''

const loadProfile = async () => {
  const userId = route.params.id
  if (!userId) { error.value = '用户ID无效'; loading.value = false; return }
  loading.value = true; error.value = null
  const r = await getUserProfile(userId)
  if (r.success && r.data) {
    profile.value = r.data
    isFollowing.value = r.data.isFollowing ?? false
    loadArticles(1)
  } else {
    error.value = r.message || '获取用户信息失败'
  }
  loading.value = false
}

const loadArticles = async (page = 1) => {
  const userId = route.params.id
  if (!userId) return
  articlesLoading.value = true
  const r = await getUserArticles(userId, { page, size: pageSize })
  if (r.success) {
    articles.value = r.data.items || []
    articlesTotalPages.value = r.data.pages || 0
    articlesPage.value = page
  }
  articlesLoading.value = false
}

const toggleFollow = async () => {
  if (!profile.value || followLoading.value) return
  followLoading.value = true
  const r = isFollowing.value
    ? await unfollowUser(profile.value.id)
    : await followUser(profile.value.id)
  if (r.success) {
    isFollowing.value = !isFollowing.value
    if (profile.value) {
      profile.value.followersCount += isFollowing.value ? 1 : -1
    }
  } else {
    alert(r.message || '操作失败')
  }
  followLoading.value = false
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const goBack = () => router.go(-1)

onMounted(() => {
  loadProfile()
  requestAnimationFrame(() => { slidIn.value = true })
})
</script>

<style lang="scss">
@use 'sass:color';
@use './_design.scss' as *;

.user-profile-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; flex: 1; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

/* 用户信息区 */
.profile-section {
  padding: $space-xl $space-xl 0;
  flex-shrink: 0;
}

.profile-header-info {
  display: flex; align-items: flex-start; gap: $space-lg;
  margin-bottom: $space-lg;
}

.profile-avatar { flex-shrink: 0; }
.avatar-img { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid $glass-border; }
.avatar-letter {
  width: 64px; height: 64px; border-radius: 50%; background: $color-primary; color: $bg-base;
  display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700;
}

.profile-detail { flex: 1; min-width: 0; }
.profile-username { font-size: 1.3rem; font-weight: 700; color: $text-primary; margin: 0 0 4px; }
.profile-role { font-size: 0.75rem; color: $color-primary; text-transform: uppercase; letter-spacing: 0.05em; }
.profile-bio { font-size: 0.9rem; color: $text-secondary; margin: 8px 0; line-height: 1.4; }

.btn-follow {
  margin-top: 8px; padding: 4px 14px; font-size: 0.85rem;
  border: 1px solid $color-primary; background: transparent; color: $color-primary;
  cursor: pointer; transition: all 0.2s;
  &:hover { background: $color-primary; color: $bg-base; }
  &.following { border-color: $color-success; color: $color-success;
    &:hover { background: $color-success; color: $bg-base; }
  }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.profile-stats-row {
  display: flex; gap: 0; border-top: 1px solid $glass-border; padding-top: $space-md;
}

.stat-cell {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px;
}
.stat-val { font-family: $font-mono; font-size: 1.1rem; font-weight: 700; color: $text-primary; }
.stat-lbl { font-size: 0.65rem; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.04em; }

/* 文章区 */
.articles-section {
  flex: 1; overflow-y: auto; padding: $space-lg $space-xl $space-xl;
}

.section-title {
  font-family: $font-mono; font-size: 0.9rem; font-weight: 600; color: $text-primary;
  margin: 0 0 $space-md; padding-bottom: $space-sm; border-bottom: 1px solid $glass-border;
}

.article-list { display: flex; flex-direction: column; gap: 4px; }

.article-row {
  padding: $space-md; cursor: pointer; transition: background 0.15s;
  &:hover { background: $bg-hover; }
}

.article-row-title { font-size: 0.95rem; font-weight: 500; color: $text-primary; margin-bottom: 4px; }
.article-row-meta { font-size: 0.78rem; color: $text-tertiary; span { margin-right: 12px; } }

.state-msg { display: flex; flex-direction: column; align-items: center; gap: $space-md; padding: $space-2xl 0; p { color: $text-secondary; font-size: 0.95rem; } }
.spinner { width: 24px; height: 24px; border: 2px solid rgba($text-tertiary, 0.25); border-top-color: $color-primary; border-radius: 50%; animation: mspin 0.8s linear infinite; }
@keyframes mspin { to { transform: rotate(360deg); } }

.pagination { display: flex; justify-content: center; align-items: center; gap: $space-md; margin-top: $space-lg; }
.page-btn { padding: 6px 16px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-secondary; cursor: pointer; font-size: 0.85rem; &:hover { color: $text-primary; border-color: $color-primary; } &:disabled { opacity: 0.4; cursor: not-allowed; } }
.page-info { font-size: 0.8rem; color: $text-tertiary; }

.btn { padding: 6px 16px; border: none; cursor: pointer; font-size: 0.9rem; }
.btn-primary { background: $color-primary; color: $bg-base; &:hover { background: color.adjust($color-primary, $lightness: 8%); } }
.btn-sm { padding: 4px 12px; font-size: 0.8rem; }
.mt-20 { margin-top: 20px; }
</style>

<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="container-narrow">
      <div class="back-button" @click="router.go(-1)">← 返回</div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载用户信息...</p>
      </div>

      <template v-else-if="profile">
        <!-- 用户信息卡片 -->
        <div class="profile-card card">
          <div class="profile-avatar">
            <img v-if="profile.avatar" :src="getAvatarUrl(profile.avatar)" class="avatar-img" />
            <span v-else class="avatar-letter">{{ (profile.username || '?').charAt(0).toUpperCase() }}</span>
          </div>
          <div class="profile-info">
            <h1 class="profile-name">{{ profile.username }}</h1>
            <p v-if="profile.bio" class="profile-bio">{{ profile.bio }}</p>
            <div class="profile-stats">
              <span>📝 {{ profile.articleCount || 0 }} 篇文章</span>
              <span>⭐ {{ profile.totalLikes || 0 }} 次获赞</span>
            </div>
          </div>
        </div>

        <!-- 文章列表 -->
        <h2 class="section-title">发布的文章</h2>

        <div v-if="articlesLoading" class="loading-state">
          <div class="loading-spinner"></div>
        </div>

        <div v-else-if="articles.length === 0" class="empty-state">
          <p>暂无已发布的文章</p>
        </div>

        <div v-else class="article-list">
          <div
            v-for="item in articles"
            :key="item.id"
            class="article-item"
            @click="router.push(`/article/${item.id}`)"
          >
            <h3 class="article-title">{{ item.title }}</h3>
            <div class="article-meta">
              <span v-if="item.category">{{ item.category.name }}</span>
              <span>{{ formatDate(item.publishedAt || item.createdAt) }}</span>
              <span>{{ item.viewCount || 0 }} 阅读</span>
            </div>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
            <span>第 {{ page }} / {{ totalPages }} 页</span>
            <button :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
          </div>
        </div>
      </template>

      <div v-else class="empty-state">
        <p>用户不存在</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUserProfile } from '@/services/userService'
import { getUserArticles } from '@/services/articleService'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const route = useRoute()
const router = useRouter()
const profile = ref(null)
const loading = ref(true)
const articles = ref([])
const articlesLoading = ref(false)
const page = ref(1)
const totalPages = ref(0)

const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const getAvatarUrl = (path) => path ? API_BASE.replace('/api/v1', '') + path : ''

const fetchArticles = async (p = 1) => {
  const userId = route.params.id
  if (!userId) return
  articlesLoading.value = true
  page.value = p
  const result = await getUserArticles(userId, { page: p, size: 10 })
  if (result.success) {
    articles.value = result.data?.items || []
    totalPages.value = result.data?.pages || 0
  }
  articlesLoading.value = false
}

const goPage = (p) => { if (p >= 1) fetchArticles(p) }

onMounted(async () => {
  const userId = route.params.id
  if (!userId) { loading.value = false; return }
  const result = await getUserProfile(userId)
  if (result.success) profile.value = result.data
  loading.value = false
  fetchArticles()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.back-button {
  display: inline-flex; align-items: center; gap: 4px;
  color: $color-primary; cursor: pointer; font-size: 0.95rem; margin: 16px 0;
}

.profile-card {
  display: flex; align-items: center; gap: 24px;
  padding: 28px 32px; margin-bottom: 32px;
}

.profile-avatar {
  flex-shrink: 0;
  .avatar-img { width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 2px solid $color-primary; }
  .avatar-letter {
    width: 72px; height: 72px; border-radius: 50%; background: $color-primary; color: $bg-base;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; font-weight: 700;
  }
}

.profile-info { flex: 1; }
.profile-name { font-size: 1.5rem; font-weight: 700; color: $text-primary; margin: 0 0 4px; }
.profile-bio { color: $text-secondary; font-size: 0.9rem; margin: 0 0 12px; }
.profile-stats { display: flex; gap: 20px; font-size: 0.85rem; color: $text-tertiary; }

.section-title { font-size: 1.3rem; font-weight: 600; color: $text-primary; margin: 0 0 16px; }

.article-item {
  padding: 16px 20px; margin-bottom: 8px;
  cursor: pointer; transition: background 0.2s;
  &:hover { background: $bg-hover; }
}
.article-title { font-size: 1.05rem; font-weight: 600; color: $text-primary; margin: 0 0 6px; }
.article-meta { display: flex; gap: 16px; font-size: 0.8rem; color: $text-tertiary; }

.pagination {
  display: flex; justify-content: center; align-items: center; gap: 16px;
  margin: 32px 0; color: $text-secondary;
  button {
    padding: 8px 20px; background: $bg-elevated; border: 1px solid $border-color-light;
    color: $text-primary; cursor: pointer;
    &:disabled { opacity: 0.4; cursor: not-allowed; }
    &:hover:not(:disabled) { border-color: $color-primary; }
  }
}

.loading-state, .empty-state { text-align: center; padding: 80px 0; color: $text-secondary; }
.loading-spinner {
  width: 28px; height: 28px; margin: 0 auto 12px;
  border: 3px solid $border-color-light; border-top-color: $color-primary;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
</style>

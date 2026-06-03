<template>
  <div class="fav-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="goBack">← 返回</button>
          <span class="card-title">我的收藏</span>
        </div>
        <div class="card-body">
          <StateWrapper :loading="loading" :empty="favorites.length === 0" empty-text="暂无收藏文章" @retry="fetchFavorites">
            <div class="fav-list">
              <div v-for="item in favorites" :key="item.id" class="fav-item">
                <div class="fav-info" @click="router.push(`/article/${item.article.id}`)">
                  <div class="fav-title">{{ item.article.title || '[无标题]' }}</div>
                  <div class="fav-meta">收藏于 {{ formatDateTime(item.createdAt) }}</div>
                </div>
                <button class="btn-unfav" @click="handleUnfavorite(item.article.id)" :disabled="unfavoritingId === item.article.id">
                  {{ unfavoritingId === item.article.id ? '取消中...' : '取消收藏' }}
                </button>
              </div>
            </div>
            <div v-if="totalPages > 1" class="pagination">
              <button class="page-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">上一页</button>
              <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页（共 {{ total }} 篇）</span>
              <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">下一页</button>
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
import { getMyFavorites, toggleFavorite } from '@/services/favoriteService'
import { formatDateTime } from '@/utils'
import StateWrapper from '@/components/StateWrapper.vue'

const router = useRouter()
const favorites = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)
const unfavoritingId = ref(null)
const slidIn = ref(false)

const fetchFavorites = async (page = 1) => {
  loading.value = true
  const r = await getMyFavorites({ page, size: pageSize.value })
  if (r.success) {
    favorites.value = r.data.items || []
    total.value = r.data.total || 0
    totalPages.value = r.data.pages || 0
    currentPage.value = page
  } else { favorites.value = [] }
  loading.value = false
}

const handleUnfavorite = async (articleId) => {
  unfavoritingId.value = articleId
  const r = await toggleFavorite(articleId)
  if (r.success) {
    favorites.value = favorites.value.filter(f => f.article.id !== articleId)
    total.value = Math.max(0, total.value - 1)
  }
  unfavoritingId.value = null
}

const goToPage = (page) => { if (page >= 1 && page <= totalPages.value) fetchFavorites(page) }
const goBack = () => router.push('/personal')

onMounted(() => { fetchFavorites(); requestAnimationFrame(() => { slidIn.value = true }) })
</script>

<style lang="scss">
@use 'sass:color';
@use './test_scss.scss' as *;

.fav-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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
  .btn-back { background: none; border: none; color: $text-secondary; cursor: pointer; font-size: 0.9rem; padding: 0; &:hover { color: $text-primary; } }
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.fav-list { display: flex; flex-direction: column; gap: 8px; }
.fav-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: $space-md; transition: background 0.15s;
  &:hover { background: $bg-hover; }
  .fav-info { flex: 1; cursor: pointer; }
  .fav-title { font-size: 1rem; font-weight: 500; color: $text-primary; margin-bottom: 4px; }
  .fav-meta { font-size: 0.8rem; color: $text-tertiary; }
}

.btn-unfav {
  padding: $space-2xs $space-md; border: 1px solid $color-error; background: transparent;
  color: $color-error; cursor: pointer; font-size: 0.8rem; white-space: nowrap; flex-shrink: 0;
  &:hover { background: $color-error; color: $bg-base; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}

.pagination { display: flex; justify-content: center; align-items: center; gap: $space-md; margin-top: $space-xl; }
.page-btn {
  padding: $space-2xs $space-md; background: $bg-elevated; border: 1px solid $glass-border;
  color: $text-secondary; cursor: pointer; font-size: 0.85rem;
  &:hover { color: $text-primary; border-color: $color-primary; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}
.page-info { font-size: 0.8rem; color: $text-tertiary; }
</style>

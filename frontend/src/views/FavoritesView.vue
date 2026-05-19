<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="back-button" @click="router.go(-1)">← 返回</div>
    <div class="container-narrow mt-30">
      <h1 class="title-large mb-30">我的收藏</h1>

      <StateWrapper :loading="loading" :empty="favorites.length === 0" empty-text="暂无收藏文章" @retry="fetchFavorites">
        <div class="article-list">
          <div v-for="item in favorites" :key="item.id" class="article-item card card-hover">
            <div class="article-info" @click="router.push(`/article/${item.article.id}`)">
              <h3 class="article-title">{{ item.article.title || '[无标题]' }}</h3>
              <div class="meta-text">
                <span>收藏于 {{ formatDateTime(item.createdAt) }}</span>
              </div>
            </div>
            <button class="btn-unfavorite" @click="handleUnfavorite(item.article.id)" :disabled="unfavoritingId === item.article.id">
              {{ unfavoritingId === item.article.id ? '取消中...' : '取消收藏' }}
            </button>
          </div>
        </div>

        <div v-if="totalPages > 1" class="pagination mt-30">
          <button class="pagination-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">上一页</button>
          <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页（共 {{ total }} 篇）</span>
          <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">下一页</button>
        </div>
      </StateWrapper>
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

const fetchFavorites = async (page = 1) => {
  loading.value = true
  const result = await getMyFavorites({ page, size: pageSize.value })
  if (result.success) {
    favorites.value = result.data.items || []
    total.value = result.data.total || 0
    totalPages.value = result.data.pages || 0
    currentPage.value = page
  } else {
    favorites.value = []
  }
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

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) fetchFavorites(page)
}

onMounted(() => fetchFavorites())
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;
.article-list { display: flex; flex-direction: column; gap: 16px; }
.article-item {
  padding: 16px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;
  transition: background 0.2s ease; &:hover { background: $bg-smoke; }
  .article-info { flex: 1; cursor: pointer; }
  .article-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 6px; color: $text-main; }
  .meta-text { font-size: 0.85rem; color: $text-secondary; span { margin-right: 8px; } }
}
.btn-unfavorite {
  padding: 6px 14px; border: 1px solid $color-danger; border-radius: 6px;
  background: white; color: $color-danger; cursor: pointer; font-size: 0.85rem; white-space: nowrap;
  &:hover { background: $color-danger; color: white; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; }
.pagination-btn { padding: 8px 16px; border: 1px solid $border-color; border-radius: 8px; background: white; cursor: pointer; font-size: 0.9rem; &:disabled { opacity: 0.4; cursor: not-allowed; } }
.page-info { font-size: 0.85rem; color: $text-secondary; }
</style>

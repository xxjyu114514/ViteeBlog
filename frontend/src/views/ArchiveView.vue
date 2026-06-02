<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="container-narrow">
      <h1 class="page-title">文章归档</h1>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载归档数据...</p>
      </div>

      <div v-else-if="archive.length === 0" class="empty-state">
        <p>暂无归档数据</p>
      </div>

      <div v-else class="archive-list">
        <div v-for="(yearGroup, yearIdx) in archive" :key="yearIdx" class="year-group">
          <h2 class="year-title">{{ yearGroup.year }}</h2>
          <div v-for="(monthGroup, mIdx) in yearGroup.months" :key="mIdx" class="month-group">
            <h3 class="month-title">{{ monthGroup.month }} 月 ({{ monthGroup.count }})</h3>
            <div
              v-for="article in monthGroup.articles"
              :key="article.id"
              class="archive-item"
              @click="goArticle(article.id)"
            >
              <span class="archive-date">{{ formatDate(article.publishedAt || article.createdAt) }}</span>
              <span class="archive-title">{{ article.title }}</span>
              <span class="archive-views">{{ article.viewCount }} 阅读</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getArticleArchive } from '@/services/articleService'

const router = useRouter()
const archive = ref([])
const loading = ref(true)

const formatDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth() + 1}-${String(date.getDate()).padStart(2, '0')}`
}

const goArticle = (id) => router.push(`/article/${id}`)

onMounted(async () => {
  const result = await getArticleArchive()
  if (result.success) {
    archive.value = result.data || []
  }
  loading.value = false
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.page-title {
  font-size: 1.8rem; font-weight: 700; color: $text-primary;
  margin: 24px 0 32px;
}

.year-group { margin-bottom: 36px; }

.year-title {
  font-size: 1.5rem; font-weight: 700; color: $color-primary;
  margin: 0 0 16px; padding-bottom: 8px;
  border-bottom: 2px solid $color-primary;
}

.month-group { margin: 0 0 20px 20px; }

.month-title {
  font-size: 1.1rem; font-weight: 600; color: $text-secondary;
  margin: 0 0 10px;
}

.archive-item {
  display: flex; align-items: center; gap: 20px;
  padding: 10px 16px; cursor: pointer; border-radius: 0;
  transition: background 0.2s;
  &:hover { background: $bg-hover; }
}

.archive-date {
  flex-shrink: 0; width: 50px;
  font-size: 0.85rem; color: $text-tertiary; font-family: $font-mono;
}

.archive-title {
  flex: 1; font-size: 0.95rem; color: $text-primary;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  &:hover { color: $color-primary; }
}

.archive-views {
  flex-shrink: 0; font-size: 0.8rem; color: $text-tertiary;
}

.loading-state, .empty-state { text-align: center; padding: 80px 0; color: $text-secondary; }

.loading-spinner {
  width: 28px; height: 28px; margin: 0 auto 12px;
  border: 3px solid $border-color-light; border-top-color: $color-primary;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
</style>

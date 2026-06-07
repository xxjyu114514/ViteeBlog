<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    <div class="container-narrow">
      <!-- 搜索框 -->
      <div class="search-bar">
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索文章标题、摘要或正文..."
          @input="onInput"
        />
        <button class="search-btn" :disabled="loading" @click="doSearch">
          {{ loading ? '搜索中...' : '搜索' }}
        </button>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searched" class="result-section">
        <p class="result-summary">
          共找到 <strong>{{ total }}</strong> 条结果
          <span v-if="keyword">（关键词：{{ keyword }}）</span>
        </p>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>搜索中...</p>
        </div>

        <div v-else-if="articles.length === 0" class="empty-state">
          <p>未找到相关文章</p>
        </div>

        <div v-else class="result-list">
          <div
            v-for="item in articles"
            :key="item.id"
            class="result-item card"
            @click="goArticle(item.id)"
          >
            <h3 class="result-title" v-html="highlight(item.title)"></h3>
            <p class="result-summary-text" v-if="item.summary" v-html="highlight(item.summary)"></p>
            <div class="result-meta">
              <span v-if="item.category">{{ item.category.name }}</span>
              <span>{{ formatDate(item.publishedAt || item.createdAt) }}</span>
              <span>{{ item.viewCount }} 阅读</span>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
          <span>第 {{ page }} / {{ totalPages }} 页</span>
          <button :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchArticles } from '@/services/articleService'

const router = useRouter()
const keyword = ref('')
const articles = ref([])
const loading = ref(false)
const searched = ref(false)
const page = ref(1)
const total = ref(0)
const totalPages = ref(0)
let debounceTimer = null

const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN') : ''

const onInput = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { doSearch() }, 400)
}

const doSearch = async (p = 1) => {
  const q = keyword.value.trim()
  if (!q) return
  loading.value = true
  searched.value = true
  page.value = p
  const result = await searchArticles({ q, page: p, size: 10 })
  if (result.success) {
    articles.value = result.data?.items || []
    total.value = result.data?.total || 0
    totalPages.value = result.data?.pages || 0
  } else {
    articles.value = []
    total.value = 0
  }
  loading.value = false
}

const goPage = (p) => { if (p >= 1) doSearch(p) }

const goArticle = (id) => router.push(`/article/${id}`)

const highlight = (text) => {
  if (!text || !keyword.value.trim()) return text
  const escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
  const regex = new RegExp(`(${keyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return escaped.replace(regex, '<mark>$1</mark>')
}

onUnmounted(() => {
  clearTimeout(debounceTimer)
  debounceTimer = null
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.search-bar {
  display: flex;
  gap: 12px;
  margin: 24px 0;
}

.search-input {
  flex: 1;
  padding: 14px 18px;
  font-size: 1.05rem;
  background: $bg-elevated;
  border: 1px solid $border-color-light;
  color: $text-primary;
  outline: none;
  transition: border-color 0.2s;
  &:focus { border-color: $color-primary; }
  &::placeholder { color: $text-tertiary; }
}

.search-btn {
  padding: 14px 28px;
  background: $color-primary;
  color: $bg-base;
  border: none;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  white-space: nowrap;
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.result-summary { color: $text-secondary; margin-bottom: 20px; font-size: 0.95rem; }

.result-item {
  padding: 20px 24px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: border-color 0.2s;
  &:hover { border-color: $color-primary; }
}

.result-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 8px;
  :deep(mark) { background: rgba($color-primary, 0.25); color: $text-primary; padding: 0 2px; }
}

.result-summary-text {
  color: $text-secondary;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 12px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  :deep(mark) { background: rgba($color-primary, 0.2); color: $text-secondary; padding: 0 2px; }
}

.result-meta {
  display: flex; gap: 16px;
  color: $text-tertiary; font-size: 0.8rem;
}

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

.loading-spinner {
  width: 28px; height: 28px; margin: 0 auto 12px;
  border: 3px solid $border-color-light; border-top-color: $color-primary;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

.loading-state, .empty-state { text-align: center; padding: 60px 0; color: $text-secondary; }
</style>

<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div class="container-narrow">
      <div class="flex-between mb-30">
        <h1 class="title-large">文章管理</h1>
        <button 
          class="btn-primary" 
          @click="handleCreateNew"
        >
          新建文章
        </button>
      </div>

      <!-- 文章列表 -->
      <div v-if="articles.length > 0" class="article-list">
        <div 
          v-for="article in articles" 
          :key="article.id" 
          class="article-item card card-hover"
        >
          <div class="flex-between">
            <div class="article-info">
              <h3 class="article-title">{{ article.title }}</h3>
              <div class="meta-text">
                <span>{{ formatDate(article.published_at || article.created_at) }}</span>
                <span v-if="article.status === 'draft'" class="status-draft">草稿</span>
                <span v-else class="status-published">已发布</span>
                <span>阅读 {{ article.view_count }} 次</span>
              </div>
            </div>
            <div class="article-actions">
              <button 
                v-if="article.status === 'draft'" 
                class="btn-action btn-publish"
                @click="handlePublish(article.id)"
                :disabled="publishingId === article.id"
              >
                {{ publishingId === article.id ? '发布中...' : '发布' }}
              </button>
              <button 
                class="btn-action btn-edit"
                @click="handleEdit(article.id)"
              >
                编辑
              </button>
              <button 
                class="btn-action btn-delete"
                @click="handleSoftDelete(article.id)"
                :disabled="deletingId === article.id"
              >
                {{ deletingId === article.id ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载文章列表中...</p>
      </div>

      <div v-else class="empty-state">
        <p>暂无文章</p>
        <button class="btn-primary mt-20" @click="handleCreateNew">立即创建第一篇文章</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleAPI } from '@/composables/useArticleAPI'

const router = useRouter()
const {
  getMyArticles,
  publishArticle,
  softDeleteArticle,
  restoreArticle
} = useArticleAPI()

// 状态管理
const loading = ref(true)
const articles = ref([])
const publishingId = ref(null)
const deletingId = ref(null)
const restoringId = ref(null)

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文章列表
const fetchArticles = async () => {
  loading.value = true
  const result = await getMyArticles()
  if (result.success) {
    articles.value = result.data.items || []
  } else {
    console.error('获取我的文章列表失败:', result.message)
  }
  loading.value = false
}

// 处理新建文章
const handleCreateNew = () => {
  router.push('/edit-article')
}

// 处理编辑文章
const handleEdit = (articleId) => {
  router.push(`/edit-article/${articleId}`)
}

// 处理发布文章
const handlePublish = async (articleId) => {
  publishingId.value = articleId
  const result = await publishArticle(articleId)
  if (result.success) {
    await fetchArticles()
  } else {
    alert(result.message)
  }
  publishingId.value = null
}

// 处理软删除
const handleSoftDelete = async (articleId) => {
  if (!confirm('确定要将此文章移至回收站吗？')) return
  
  deletingId.value = articleId
  const result = await softDeleteArticle(articleId)
  if (result.success) {
    await fetchArticles()
  } else {
    alert(result.message)
  }
  deletingId.value = null
}

// 处理恢复文章
const handleRestore = async (articleId) => {
  restoringId.value = articleId
  const result = await restoreArticle(articleId)
  if (result.success) {
    await fetchArticles()
  } else {
    alert(result.message)
  }
  restoringId.value = null
}

// 初始化
onMounted(async () => {
  await fetchArticles()
})
</script>
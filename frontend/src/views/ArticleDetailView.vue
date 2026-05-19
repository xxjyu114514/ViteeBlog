<template>
  <div class="page-wrapper-base">
    <div class="nav-placeholder"></div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载文章中...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <h2 class="error-title">文章加载失败</h2>
        <p class="error-message">{{ error }}</p>
        <button class="btn-primary mt-20" @click="loadArticle">
          重新加载
        </button>
        <button class="btn-secondary mt-10" @click="goBack">
          返回首页
        </button>
      </div>
    </div>
    
    <div v-else-if="article" class="article-detail-container">
      <div class="back-button" @click="handleBack">
        ← 返回
      </div>
      
      <div class="container-narrow">
        <div class="article-header">
          <h1 class="article-title" v-html="renderedTitle"></h1>
          <div class="article-meta flex-between">
            <div class="meta-info">
              <span class="author">作者: {{ getAuthorName() }}</span>
              <span class="publish-date">{{ formatDateTime(article.publishedAt) }}</span>
              <span class="view-count">阅读: {{ article.viewCount || 0 }} 次</span>
            </div>
            <div v-if="userStore.isAdmin" class="admin-actions">
              <button class="btn-action btn-edit" @click="editArticle">
                编辑
              </button>
              <button 
                class="btn-action btn-delete" 
                @click="deleteArticle"
                :disabled="deleting"
              >
                {{ deleting ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="article-content" v-html="renderedContent"></div>
        
        <!-- 评论区 -->
        <div class="comment-section">
          <div class="section-header">
            <h2 class="title">评论区</h2>
            <span class="count">{{ commentCount }} 条评论</span>
          </div>
          
          <CommentForm 
            :article-id="route.params.id" 
            @comment-submitted="handleNewComment"
          />
          
          <CommentList 
            :article-id="route.params.id"
            @comments-loaded="updateCommentCount"
            ref="commentListRef"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getArticleDetail as fetchArticleDetail, softDeleteArticle, loadArticleContent } from '@/services/articleService'
import CommentForm from '@/components/CommentForm.vue'
import CommentList from '@/components/CommentList.vue'
import { formatDateTime, renderMarkdown, renderInline } from '@/utils'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const article = ref(null)
const articleContent = ref('')
const loading = ref(true)
const error = ref(null)
const deleting = ref(false)
const commentCount = ref(0)
const commentListRef = ref(null)

const getAuthorName = () => {
  if (article.value?.author?.username) return article.value.author.username
  if (article.value?.userId) return `用户${article.value.userId}`
  return '匿名作者'
}

const renderedContent = computed(() => {
  if (!articleContent.value) return ''
  return renderMarkdown(articleContent.value)
})

const renderedTitle = computed(() => {
  if (!article.value?.title) return ''
  return renderInline(article.value.title)
})

const loadArticle = async () => {
  loading.value = true
  error.value = null
  const articleId = route.params.id
  const result = await fetchArticleDetail(articleId)
  if (result.success) {
    article.value = result.data
    if (result.data.contentPath) {
      const contentResult = await loadArticleContent(result.data.contentPath)
      articleContent.value = contentResult.success ? contentResult.data : (result.data.content || '')
    } else {
      articleContent.value = result.data.content || ''
    }
  } else {
    error.value = result.message
  }
  loading.value = false
}

const updateCommentCount = (count) => { commentCount.value = count }

const handleNewComment = () => {
  if (commentListRef.value) {
    setTimeout(() => { commentListRef.value.refreshComments() }, 300)
  }
}

const editArticle = () => router.push(`/edit-article/${route.params.id}`)

const deleteArticle = async () => {
  if (!confirm('确定要将此文章移至回收站吗？')) return
  deleting.value = true
  const result = await softDeleteArticle(route.params.id)
  if (result.success) {
    alert('文章已移至回收站')
    router.push('/posts')
  } else {
    alert(result.message)
  }
  deleting.value = false
}

const goBack = () => router.push('/')
const handleBack = () => router.go(-1)

onMounted(() => { loadArticle() })
</script>

<style scoped lang="scss">
@use '@/assets/styles/components/comment';

.article-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-button {
  margin-bottom: 24px;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.article-header {
  margin-bottom: 32px;
}

.article-title {
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 16px;
  color: #1f2937;
}

.article-meta {
  .meta-info {
    display: flex;
    gap: 16px;
    color: #6b7280;
    font-size: 0.95rem;
  }
  
  .admin-actions {
    display: flex;
    gap: 12px;
  }
  
  .btn-action {
    padding: 6px 16px;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    
    &.btn-edit {
      background: #dbeafe;
      color: #2563eb;
      &:hover { background: #bfdbfe; }
    }
    
    &.btn-delete {
      background: #fee2e2;
      color: #dc2626;
      &:hover:not(:disabled) { background: #fecaca; }
      &:disabled { opacity: 0.6; cursor: not-allowed; }
    }
  }
}

.article-content {
  margin-bottom: 60px;
  line-height: 1.7;
  color: #374151;
  
  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.3;
  }
  :deep(h1) { font-size: 1.8rem; }
  :deep(h2) { font-size: 1.5rem; }
  :deep(h3) { font-size: 1.25rem; }
  :deep(h4) { font-size: 1.125rem; }
  
  :deep(p) { margin-bottom: 16px; }
  :deep(img) { max-width: 100%; height: auto; margin: 24px 0; border-radius: 8px; }
  
  :deep(blockquote) {
    margin: 24px 0; padding: 16px 24px;
    border-left: 4px solid #3b82f6; background: #f8fafc;
    color: #374151; font-style: italic;
  }
  
  :deep(code) {
    padding: 2px 6px; background: #f1f5f9;
    border-radius: 4px; font-family: monospace; font-size: 0.9em;
  }
  
  :deep(pre) {
    margin: 24px 0; padding: 20px;
    background: #1e293b; border-radius: 8px; overflow-x: auto;
    code { background: none; padding: 0; color: #f8fafc; }
  }
  
  :deep(ul), :deep(ol) { margin: 16px 0; padding-left: 24px; li { margin-bottom: 8px; } }
  :deep(a) { color: #3b82f6; text-decoration: none; &:hover { text-decoration: underline; } }
}
</style>

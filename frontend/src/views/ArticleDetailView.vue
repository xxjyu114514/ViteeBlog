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
              <span class="publish-date">{{ formatDate(article.published_at) }}</span>
              <span class="view-count">阅读: {{ article.view_count || 0 }} 次</span>
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
          
          <!-- 评论表单 -->
          <CommentForm 
            :article-id="route.params.id" 
            @comment-submitted="handleNewComment"
          />
          
          <!-- 评论列表 -->
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
import MarkdownIt from 'markdown-it'
import { getBaseUrl } from '@/api/config'
import { useUserStore } from '@/stores/user'
import { useArticleAPI } from '@/composables/useArticleAPI'
import CommentForm from '@/components/CommentForm.vue'
import CommentList from '@/components/CommentList.vue'

// 初始化Markdown解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { getArticleDetail, softDeleteArticle } = useArticleAPI()

// 状态
const article = ref(null)
const articleContent = ref('') // 新增：存储从文件读取的Markdown内容
const loading = ref(true)
const error = ref(null)
const deleting = ref(false)
const commentCount = ref(0)
const commentListRef = ref(null)

// 获取作者名称（处理author关系可能未加载的情况）
const getAuthorName = () => {
  if (article.value?.author?.username) {
    return article.value.author.username
  }
  // 如果author关系未加载，尝试从其他字段获取
  if (article.value?.user_id) {
    // 这里可以添加逻辑来根据user_id获取用户名，但需要额外API调用
    // 临时方案：显示用户ID或默认名称
    return `用户${article.value.user_id}`
  }
  return '匿名作者'
}

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

// 渲染内容
const renderedContent = computed(() => {
  if (!articleContent.value) return ''
  return md.render(articleContent.value)
})

const renderedTitle = computed(() => {
  if (!article.value?.title) return ''
  return md.renderInline(article.value.title)
})

// 从文件路径加载Markdown内容
const loadArticleContent = async (contentPath) => {
  try {
    const backendBaseUrl = getBaseUrl().replace('/api/v1', '')
    
    // 尝试标准化路径（统一使用正斜杠）
    let normalizedPath = contentPath.replace(/\\/g, '/')
    if (!normalizedPath.startsWith('/')) {
      normalizedPath = '/' + normalizedPath
    }
    const normalizedUrl = `${backendBaseUrl}${normalizedPath}`
    
    // 首先尝试标准化路径
    let response = await fetch(normalizedUrl)
    if (response.ok) {
      const content = await response.text()
      articleContent.value = content
      return true
    }
    
    // 如果标准化路径失败，尝试原始路径（以防特殊情况）
    const originalUrl = `${backendBaseUrl}/${contentPath.replace(/^\/+/, '')}`
    response = await fetch(originalUrl)
    if (response.ok) {
      const content = await response.text()
      articleContent.value = content
      return true
    }
    
    console.error('加载文章内容失败: 两种路径格式都尝试了但文件不存在')
    return false
  } catch (err) {
    console.error('加载文章内容异常:', err)
    return false
  }
}

// 加载文章
const loadArticle = async () => {
  loading.value = true
  error.value = null
  
  const articleId = route.params.id
  const result = await getArticleDetail(articleId)
  
  if (result.success) {
    article.value = result.data
    // 从 content_path 加载实际内容
    if (result.data.content_path) {
      const loadedFromFile = await loadArticleContent(result.data.content_path)
      if (!loadedFromFile) {
        // 文件加载失败，回退到数据库content字段
        articleContent.value = result.data.content || ''
        console.log('⚠️ 文件加载失败，使用数据库content字段')
      }
    } else {
      articleContent.value = result.data.content || ''
    }
  } else {
    error.value = result.message
  }
  loading.value = false
}

// 更新评论数量
const updateCommentCount = (count) => {
  commentCount.value = count
}

// 处理新评论
const handleNewComment = (newComment) => {
  // 刷新评论列表
  if (commentListRef.value) {
    // 添加短暂延迟确保后端数据已更新
    setTimeout(() => {
      commentListRef.value.refreshComments()
    }, 300)
  }
}

// 编辑文章
const editArticle = () => {
  router.push(`/edit-article/${route.params.id}`)
}

// 删除文章
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

// 返回首页
const goBack = () => {
  router.push('/')
}

// 返回上一页
const handleBack = () => {
  router.go(-1)
}

// 初始化
onMounted(() => {
  loadArticle()
})
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
      
      &:hover {
        background: #bfdbfe;
      }
    }
    
    &.btn-delete {
      background: #fee2e2;
      color: #dc2626;
      
      &:hover:not(:disabled) {
        background: #fecaca;
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
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
  
  :deep(p) {
    margin-bottom: 16px;
  }
  
  :deep(img) {
    max-width: 100%;
    height: auto;
    margin: 24px 0;
    border-radius: 8px;
  }
  
  :deep(blockquote) {
    margin: 24px 0;
    padding: 16px 24px;
    border-left: 4px solid #3b82f6;
    background: #f8fafc;
    color: #374151;
    font-style: italic;
  }
  
  :deep(code) {
    padding: 2px 6px;
    background: #f1f5f9;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9em;
  }
  
  :deep(pre) {
    margin: 24px 0;
    padding: 20px;
    background: #1e293b;
    border-radius: 8px;
    overflow-x: auto;
    
    code {
      background: none;
      padding: 0;
      color: #f8fafc;
    }
  }
  
  :deep(ul), :deep(ol) {
    margin: 16px 0;
    padding-left: 24px;
    
    li {
      margin-bottom: 8px;
    }
  }
  
  :deep(a) {
    color: #3b82f6;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
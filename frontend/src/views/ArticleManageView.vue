<template>
  <div class="page-wrapper-base article-manage-wrapper">
    <div class="nav-placeholder"></div>
    
    <div class="back-button" @click="handleBack">
      ← 返回
    </div>
    
    <div class="container-narrow">
      <div class="flex-between mb-30">
        <h1 class="title-large">{{ userStore.isAdmin ? '全站文章管理' : '我的文章' }}</h1>
        <button 
          class="btn-primary" 
          @click="handleCreateNew"
        >
          新建文章
        </button>
      </div>

      <!-- 管理员专属功能 -->
      <div v-if="userStore.isAdmin" class="admin-controls mb-20">
        <div class="flex-between">
          <div>
            <label class="mr-10">查看范围:</label>
            <select v-model="viewMode" class="select-field" @change="fetchArticles(1)">
              <option value="all">全站文章</option>
              <option value="mine">我的文章</option>
            </select>
          </div>
          <div class="admin-nav-links">
            <router-link to="/comment-reports" class="nav-link">
              举报管理
            </router-link>
            <router-link to="/comment-admin" class="nav-link">
              评论巡查
            </router-link>
          </div>
        </div>
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
                <span v-if="userStore.isAdmin && viewMode === 'all' && article.author">{{ article.author.username }} · </span>
                <span>{{ formatDate(article.published_at || article.created_at) }}</span>
                <span v-if="article.status === 'draft'" class="status-draft">草稿</span>
                <span v-else class="status-published">已发布</span>
                <span>阅读 {{ article.view_count }} 次</span>
                <span v-if="article.is_audited" class="status-audited">✓ 已审核</span>
              </div>
            </div>
            <div class="article-actions">
              <button 
                v-if="canPublish(article)"
                class="btn-action btn-publish"
                @click="handlePublish(article.id)"
                :disabled="publishingId === article.id"
              >
                {{ publishingId === article.id ? '发布中...' : '发布' }}
              </button>
              <button 
                v-if="canEdit(article)"
                class="btn-action btn-edit"
                @click="handleEdit(article.id)"
              >
                编辑
              </button>
              <button 
                v-if="canDelete(article)"
                class="btn-action btn-delete"
                @click="handleSoftDelete(article.id)"
                :disabled="deletingId === article.id"
              >
                {{ deletingId === article.id ? '删除中...' : '删除' }}
              </button>
              <button 
                v-if="userStore.isAdmin && !article.is_audited && article.status === 'pending'"
                class="btn-action btn-audit"
                @click="showAuditDialog(article.id)"
                :disabled="auditingId === article.id"
              >
                {{ auditingId === article.id ? '审核中...' : '审核' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 分页导航 -->
        <div v-if="totalPages > 1" class="pagination mt-30">
          <button 
            class="pagination-btn" 
            :disabled="currentPage <= 1"
            @click="goToPage(currentPage - 1)"
          >
            上一页
          </button>
          
          <span class="page-info">
            第 {{ currentPage }} 页 / 共 {{ totalPages }} 页 (共 {{ totalArticles }} 篇文章)
          </span>
          
          <button 
            class="pagination-btn" 
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 审核对话框 -->
      <div v-if="auditDialog.show" class="modal-overlay" @click="closeAuditDialog">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">审核文章</h3>
            <button class="modal-close" @click="closeAuditDialog">&times;</button>
          </div>
          <div class="modal-body">
            <!-- 文章预览区域 -->
            <div class="article-preview-section mb-20">
              <h4 class="preview-title">文章预览</h4>
              
              <!-- 加载状态 -->
              <div v-if="auditDialog.loadingArticle" class="preview-loading">
                <div class="loading-spinner"></div>
                <p>加载文章内容中...</p>
              </div>
              
              <!-- 预览内容 -->
              <div v-else-if="auditDialog.articleData" class="preview-content">
                <div class="preview-header">
                  <h3 class="preview-article-title">{{ auditDialog.articleData.title || '[无标题]' }}</h3>
                  <div class="preview-meta">
                    <span v-if="auditDialog.articleData.author">作者：{{ auditDialog.articleData.author.username }}</span>
                    <span>提交时间：{{ formatDate(auditDialog.articleData.submitted_at || auditDialog.articleData.created_at) }}</span>
                    <span v-if="auditDialog.articleData.category">分类：{{ auditDialog.articleData.category.name }}</span>
                  </div>
                </div>
                
                <div class="preview-summary" v-if="auditDialog.articleData.summary">
                  <strong>摘要：</strong>{{ auditDialog.articleData.summary }}
                </div>
                
                <div class="preview-content-area">
                  <h5>文章内容：</h5>
                  <div class="markdown-content" v-html="renderMarkdown(auditDialog.articleData.content)"></div>
                </div>
              </div>
              
              <div v-else class="preview-error">
                <p>无法加载文章预览</p>
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">审核结果:</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input 
                    type="radio" 
                    v-model="auditDialog.passAudit" 
                    :value="true"
                  />
                  <span class="radio-text">✅ 通过审核</span>
                </label>
                <label class="radio-option">
                  <input 
                    type="radio" 
                    v-model="auditDialog.passAudit" 
                    :value="false"
                  />
                  <span class="radio-text">❌ 驳回文章</span>
                </label>
              </div>
            </div>
            
            <div v-if="!auditDialog.passAudit" class="form-group">
              <label class="form-label">驳回原因:</label>
              <textarea 
                v-model="auditDialog.remark"
                class="textarea-field"
                placeholder="请输入驳回原因..."
                rows="4"
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <div class="modal-actions">
              <button class="btn-secondary" @click="closeAuditDialog">取消</button>
              <button 
                class="btn-primary" 
                @click="handleAudit"
                :disabled="auditingId === auditDialog.articleId"
              >
                {{ auditingId === auditDialog.articleId ? '审核中...' : '确认审核' }}
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
        <p>{{ emptyMessage }}</p>
        <button class="btn-primary mt-20" @click="handleCreateNew">立即创建第一篇文章</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useArticleAPI } from '@/composables/useArticleAPI'
import { getBaseUrl } from '@/api/config'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

// 初始化Markdown解析器（用于预览）
const mdPreview = new MarkdownIt({
  html: true,
  linkify: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(str, { language: lang }).value
    }
    return ''
  }
})

// Markdown渲染函数
const renderMarkdown = (content) => {
  if (!content) return ''
  return mdPreview.render(content)
}

const router = useRouter()
const userStore = useUserStore()
const {
  getMyArticles,
  getAdminAllArticles,
  publishArticle,
  softDeleteArticle,
  restoreArticle,
  reviewArticle
} = useArticleAPI()

// 状态管理
const loading = ref(true)
const articles = ref([])
const publishingId = ref(null)
const deletingId = ref(null)
const restoringId = ref(null)
const auditingId = ref(null)
const auditDialog = ref({
  show: false,
  articleId: null,
  passAudit: true,
  remark: '',
  articleData: null, // 新增：存储文章详情数据
  loadingArticle: false // 新增：加载状态
})
const viewMode = ref('all') // 'mine' | 'all'
const currentPage = ref(1)
const pageSize = ref(20)
const totalArticles = ref(0)

// 计算属性
const emptyMessage = computed(() => {
  if (userStore.isAdmin) {
    return viewMode.value === 'all' ? '全站暂无文章' : '您暂无文章'
  }
  return '您暂无文章'
})

const totalPages = computed(() => {
  return Math.ceil(totalArticles.value / pageSize.value)
})

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

// 权限检查函数
const canEdit = (article) => {
  return userStore.isAdmin || article.user_id === userStore.userInfo?.id
}

const canDelete = (article) => {
  return userStore.isAdmin || article.user_id === userStore.userInfo?.id
}

const canPublish = (article) => {
  return article.status === 'draft' && (userStore.isAdmin || article.user_id === userStore.userInfo?.id)
}

// 获取文章列表
const fetchArticles = async (page = 1) => {
  loading.value = true
  
  try {
    let result
    if (userStore.isAdmin && viewMode.value === 'all') {
      // 管理员查看全站文章 - 修正参数顺序：status, page, size
      // 如果要获取所有状态的文章，status 应该为 null
      result = await getAdminAllArticles(null, page, pageSize.value)
    } else {
      // 查看自己的文章（也支持分页）
      result = await getMyArticles(page, pageSize.value)
    }
    
    if (result.success) {
      articles.value = result.data.items || []
      totalArticles.value = result.data.total || 0
      currentPage.value = page
    } else {
      console.error('获取文章列表失败:', result.message)
      alert(result.message)
    }
  } catch (error) {
    console.error('获取文章列表异常:', error)
    alert('获取文章列表失败，请稍后重试')
  }
  
  loading.value = false
}

// 处理新建文章
const handleCreateNew = () => {
  router.push('/edit-article')
}

// 处理编辑文章
const handleEdit = (articleId) => {
  // 检查是否为无效的ID
  const isInvalidId = !articleId || 
    articleId === 'undefined' || 
    articleId === 'null' || 
    articleId === '';
    
  if (isInvalidId) {
    console.error('编辑文章失败：缺少有效的文章ID', articleId)
    alert('无法编辑此文章，请刷新页面重试')
    return
  }
  router.push(`/edit-article/${articleId}`)
}

// 处理发布文章
const handlePublish = async (articleId) => {
  publishingId.value = articleId
  const result = await publishArticle(articleId)
  if (result.success) {
    await fetchArticles(currentPage.value)
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
    await fetchArticles(currentPage.value)
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
    await fetchArticles(currentPage.value)
  } else {
    alert(result.message)
  }
  restoringId.value = null
}

// 显示审核对话框
const showAuditDialog = async (articleId) => {
  auditDialog.value = {
    show: false,
    articleId: null,
    passAudit: true,
    remark: '',
    articleData: null,
    loadingArticle: true
  }
  
  // 先加载文章详情
  const { getArticleDetail } = useArticleAPI()
  const result = await getArticleDetail(articleId)
  
  if (result.success) {
    // 加载文章内容文件
    let contentToLoad = ''
    const info = result.data
    if (info.content_path) {
      try {
        const backendBaseUrl = getBaseUrl().replace('/api/v1', '')
        let normalizedPath = info.content_path.replace(/\\/g, '/')
        if (!normalizedPath.startsWith('/')) {
          normalizedPath = '/' + normalizedPath
        }
        const normalizedUrl = `${backendBaseUrl}${normalizedPath}`
        
        let contentResponse = await fetch(normalizedUrl)
        if (contentResponse.ok) {
          contentToLoad = await contentResponse.text()
        } else {
          // 尝试原始路径
          const originalUrl = `${backendBaseUrl}/${info.content_path.replace(/^\/+/, '')}`
          contentResponse = await fetch(originalUrl)
          if (contentResponse.ok) {
            contentToLoad = await contentResponse.text()
          }
        }
      } catch (err) {
        console.error('加载文章内容失败:', err)
        contentToLoad = '[内容加载失败]'
      }
    }
    
    // 合并内容到文章数据
    const articleWithContent = {
      ...info,
      content: contentToLoad || info.summary || '[无内容]'
    }
    
    auditDialog.value = {
      show: true,
      articleId: articleId,
      passAudit: true,
      remark: '',
      articleData: articleWithContent,
      loadingArticle: false
    }
  } else {
    alert('加载文章详情失败：' + result.message)
    auditDialog.value.loadingArticle = false
  }
}

// 处理审核文章（管理员专属）
const handleAudit = async () => {
  if (!auditDialog.value.show || !auditDialog.value.articleId) return
  
  auditingId.value = auditDialog.value.articleId
  try {
    // 使用正确的API接口
    const result = await reviewArticle(
      auditDialog.value.articleId, 
      auditDialog.value.passAudit, 
      auditDialog.value.remark
    )
    
    if (result.success) {
      await fetchArticles(currentPage.value)
      auditDialog.value.show = false
    } else {
      alert(result.message || '审核操作失败')
    }
  } catch (error) {
    console.error('审核文章异常:', error)
    alert('审核操作失败，请稍后重试')
  } finally {
    auditingId.value = null
  }
}

// 关闭审核对话框
const closeAuditDialog = () => {
  auditDialog.value.show = false
}

// 分页导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchArticles(page)
  }
}

// 初始化
onMounted(async () => {
  // 管理员默认查看全站文章，普通用户只能查看自己的文章
  if (!userStore.isAdmin) {
    viewMode.value = 'mine'
  }
  await fetchArticles(1)
})

// 返回上一页
const handleBack = () => {
  router.go(-1)
}
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.article-manage-wrapper {
  padding-top: 100px;
}

.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  padding: 8px 16px;
  background: rgba($color-primary, 0.1);
  color: $color-primary;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba($color-primary, 0.2);
    transform: translateY(-1px);
  }
}

.admin-controls {
  padding: 16px;
  background: rgba($color-primary, 0.05);
  border-radius: 8px;
  
  .admin-nav-links {
    display: flex;
    gap: 16px;
    
    .nav-link {
      display: inline-block;
      padding: 8px 16px;
      background: rgba($color-primary, 0.1);
      color: $color-primary;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 500;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba($color-primary, 0.2);
        transform: translateY(-1px);
      }
    }
  }
}

.article-list {
  .article-item {
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .article-info {
      .article-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 8px;
      }
      
      .meta-text {
        font-size: 0.875rem;
        color: $color-secondary;
        span {
          margin-right: 8px;
        }
        
        .status-draft {
          color: $color-warning;
        }
        
        .status-published {
          color: $color-success;
        }
        
        .status-audited {
          color: $color-primary;
        }
      }
    }
    
    .article-actions {
      .btn-action {
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        
        &:hover {
          transform: translateY(-1px);
        }
      }
      
      .btn-publish {
        background: rgba($color-success, 0.1);
        color: $color-success;
        
        &:hover {
          background: rgba($color-success, 0.2);
        }
      }
      
      .btn-edit {
        background: rgba($color-primary, 0.1);
        color: $color-primary;
        
        &:hover {
          background: rgba($color-primary, 0.2);
        }
      }
      
      .btn-delete {
        background: rgba($color-danger, 0.1);
        color: $color-danger;
        
        &:hover {
          background: rgba($color-danger, 0.2);
        }
      }
      
      .btn-audit {
        background: rgba($color-primary, 0.1);
        color: $color-primary;
        
        &:hover {
          background: rgba($color-primary, 0.2);
        }
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  
  .pagination-btn {
    padding: 8px 16px;
    background: rgba($color-primary, 0.1);
    color: $color-primary;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba($color-primary, 0.2);
      transform: translateY(-1px);
    }
    
    &:disabled {
      background: rgba($color-secondary, 0.1);
      color: $color-secondary;
      cursor: not-allowed;
    }
  }
  
  .page-info {
    font-size: 0.875rem;
    color: $color-secondary;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: $color-bg;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  .modal-title {
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: $color-secondary;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      color: $color-primary;
    }
  }
}

.modal-body {
  .article-preview-section {
    .preview-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 16px;
    }
    
    .preview-loading {
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
      gap: 8px;
      
      .loading-spinner {
        width: 32px;
        height: 32px;
        border: 4px solid rgba($color-primary, 0.1);
        border-top: 4px solid $color-primary;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
    }
    
    .preview-content {
      .preview-header {
        .preview-article-title {
          font-size: 1.125rem;
          font-weight: 600;
          margin-bottom: 8px;
        }
        
        .preview-meta {
          font-size: 0.875rem;
          color: $color-secondary;
          span {
            margin-right: 8px;
          }
        }
      }
      
      .preview-summary {
        font-size: 0.875rem;
        color: $color-secondary;
        margin-bottom: 16px;
      }
      
      .preview-content-area {
        pre {
          background: rgba($color-secondary, 0.1);
          padding: 16px;
          border-radius: 8px;
          font-family: monospace;
          white-space: pre-wrap;
          overflow-x: auto;
        }
      }
    }
    
    .preview-error {
      p {
        color: $color-danger;
      }
    }
  }
  
  .form-group {
    margin-bottom: 16px;
    
    .form-label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      margin-bottom: 8px;
    }
    
    .radio-group {
      display: flex;
      gap: 16px;
      
      .radio-option {
        display: flex;
        align-items: center;
        
        input[type="radio"] {
          margin-right: 8px;
        }
        
        .radio-text {
          font-size: 0.875rem;
          color: $color-secondary;
        }
      }
    }
    
    .textarea-field {
      width: 100%;
      padding: 12px;
      border: 1px solid rgba($color-secondary, 0.3);
      border-radius: 8px;
      font-size: 0.875rem;
      color: $color-secondary;
      resize: vertical;
    }
  }
}

.modal-footer {
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 16px;
    
    .btn-secondary {
      padding: 8px 16px;
      background: rgba($color-secondary, 0.1);
      color: $color-secondary;
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba($color-secondary, 0.2);
        transform: translateY(-1px);
      }
    }
    
    .btn-primary {
      padding: 8px 16px;
      background: rgba($color-primary, 0.1);
      color: $color-primary;
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba($color-primary, 0.2);
        transform: translateY(-1px);
      }
    }
  }
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 16px;
  margin-top: 50px;
  
  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 4px solid rgba($color-primary, 0.1);
    border-top: 4px solid $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 16px;
  margin-top: 50px;
  
  p {
    font-size: 1rem;
    color: $color-secondary;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

</style>
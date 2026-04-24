<template>
  <div class="page-wrapper-base">
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
                v-if="userStore.isAdmin && !article.is_audited && article.status === 'published'"
                class="btn-action btn-audit"
                @click="handleAudit(article.id)"
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

const router = useRouter()
const userStore = useUserStore()
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
const auditingId = ref(null)
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

// 获取全站文章（管理员专用）
const getAdminAllArticles = async (page = 1, size = 20) => {
  try {
    const url = `http://127.0.0.1:8000/api/v1/article/admin/all-articles?page=${page}&size=${size}`
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      return { success: true, data }
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '获取全站文章失败'
      return { success: false, message: errorMessage }
    }
  } catch (error) {
    console.error('获取全站文章异常:', error)
    return { success: false, message: '网络错误，请稍后重试' }
  }
}

// 获取文章列表
const fetchArticles = async (page = 1) => {
  loading.value = true
  
  try {
    let result
    if (userStore.isAdmin && viewMode.value === 'all') {
      // 管理员查看全站文章
      result = await getAdminAllArticles(page, pageSize.value)
    } else {
      // 查看自己的文章（也支持分页）
      const url = `http://127.0.0.1:8000/api/v1/article/user/my-articles?page=${page}&size=${pageSize.value}`
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        result = { success: true, data }
      } else {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || '获取我的文章失败'
        result = { success: false, message: errorMessage }
      }
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

// 处理审核文章（管理员专属）
const handleAudit = async (articleId) => {
  auditingId.value = articleId
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/article/admin/articles/${articleId}/audit`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      await fetchArticles(currentPage.value)
    } else {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || '审核失败'
      alert(errorMessage)
    }
  } catch (error) {
    console.error('审核文章异常:', error)
    alert('审核失败，请稍后重试')
  }
  auditingId.value = null
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

<style scoped>
.admin-controls {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.select-field {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
  font-size: 14px;
}

.mr-10 {
  margin-right: 10px;
}

.article-list {
  margin-top: 20px;
}

.article-item {
  padding: 20px;
  margin-bottom: 15px;
  border-radius: 8px;
}

.article-info {
  flex: 1;
}

.article-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.meta-text {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #666;
  font-size: 14px;
}

.status-draft {
  background: #fef3c7;
  color: #92400e;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-published {
  background: #d1fae5;
  color: #065f46;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-audited {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 8px;
}

.article-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-action {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  border: none;
  cursor: pointer;
}

.btn-publish {
  background-color: #3b82f6;
  color: white;
}

.btn-publish:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-publish:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.btn-edit {
  background-color: #8b5cf6;
  color: white;
}

.btn-edit:hover {
  background-color: #7c3aed;
}

.btn-delete {
  background-color: #ef4444;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-delete:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.btn-audit {
  background-color: #10b981;
  color: white;
}

.btn-audit:hover:not(:disabled) {
  background-color: #059669;
}

.btn-audit:disabled {
  background-color: #a7f3d0;
  cursor: not-allowed;
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.mt-20 {
  margin-top: 20px;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e5e7eb;
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

.mt-30 {
  margin-top: 30px;
}
</style>
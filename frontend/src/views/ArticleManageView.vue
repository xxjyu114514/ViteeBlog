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
  remark: ''
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
      // 管理员查看全站文章
      result = await getAdminAllArticles(page, pageSize.value, false)
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
const showAuditDialog = (articleId) => {
  auditDialog.value = {
    show: true,
    articleId: articleId,
    passAudit: true,
    remark: ''
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

<style scoped>
/* 所有内联样式已移除，使用_base.scss中的通用类 */
</style>
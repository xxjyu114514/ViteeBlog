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
                <span>{{ formatDateTime(article.publishedAt || article.createdAt) }}</span>
                <span v-if="article.status === 'draft'" class="status-draft">草稿</span>
                <span v-else class="status-published">已发布</span>
                <span>阅读 {{ article.viewCount || 0 }} 次</span>
                <span v-if="article.isAudited" class="status-audited">✓ 已审核</span>
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
                v-if="userStore.isAdmin && !article.isAudited && article.status === 'pending'"
                class="btn-action btn-audit"
                @click="openAudit(article.id)"
              >
                审核
              </button>
            </div>
          </div>
        </div>

        <div v-if="totalPages > 1" class="pagination mt-30">
          <button class="pagination-btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">上一页</button>
          <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页 (共 {{ totalArticles }} 篇文章)</span>
          <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">下一页</button>
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

    <AuditModal v-model:show="showAuditModal" :article-id="auditArticleId" @audit-success="onAuditSuccess" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import * as articleService from '@/services/articleService'
import { formatDateTime } from '@/utils'
import AuditModal from '@/components/AuditModal.vue'

const router = useRouter()
const userStore = useUserStore()

// 状态管理
const loading = ref(true)
const articles = ref([])
const publishingId = ref(null)
const deletingId = ref(null)
const restoringId = ref(null)
const auditArticleId = ref(null)
const showAuditModal = ref(false)
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

// 权限检查函数
const canEdit = (article) => {
  return userStore.isAdmin || article.userId === userStore.userInfo?.id
}

const canDelete = (article) => {
  return userStore.isAdmin || article.userId === userStore.userInfo?.id
}

const canPublish = (article) => {
  return article.status === 'draft' && (userStore.isAdmin || article.userId === userStore.userInfo?.id)
}

// 获取文章列表
const fetchArticles = async (page = 1) => {
  loading.value = true
  
  try {
    let result
    if (userStore.isAdmin && viewMode.value === 'all') {
      // 管理员查看全站文章 - 修正参数顺序：status, page, size
      // 如果要获取所有状态的文章，status 应该为 null
      result = await articleService.getAdminAllArticles({ page, size: pageSize.value })
    } else {
      // 查看自己的文章（也支持分页）
      result = await articleService.getMyArticles({ page, size: pageSize.value })
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
  const result = await articleService.publishArticle(articleId)
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
  const result = await articleService.softDeleteArticle(articleId)
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
  const result = await articleService.restoreArticle(articleId)
  if (result.success) {
    await fetchArticles(currentPage.value)
  } else {
    alert(result.message)
  }
  restoringId.value = null
}

// 审核弹窗
const openAudit = (articleId) => {
  auditArticleId.value = articleId
  showAuditModal.value = true
}
const onAuditSuccess = () => {
  fetchArticles(currentPage.value)
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
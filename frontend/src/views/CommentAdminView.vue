<template>
  <div class="comment-admin-container">
    <div class="page-header">
      <h1>评论巡查</h1>
      <p class="subtitle">全站评论管理与审核</p>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="toolbar">
      <div class="filter-section">
        <label for="status-filter">状态筛选：</label>
        <select 
          id="status-filter" 
          v-model="filterStatus"
          @change="handleFilterChange"
          class="filter-select"
        >
          <option value="all">全部评论</option>
          <option value="pending">违规评论</option>
          <option value="approved">正常评论</option>
          <option value="deleted">已删除评论</option>
        </select>
      </div>

      <div class="action-section" v-if="selectedComments.length > 0">
        <span class="selection-info">已选择 {{ selectedComments.length }} 条评论</span>
        <button 
          class="btn-batch-approve" 
          @click="handleBatchApprove"
          :disabled="batchLoading"
        >
          {{ batchLoading ? '处理中...' : '批量恢复显示' }}
        </button>
        <button 
          class="btn-batch-reject" 
          @click="handleBatchReject"
          :disabled="batchLoading"
        >
          {{ batchLoading ? '处理中...' : '批量标记违规' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="pendingComments.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>暂无待审核评论</h3>
      <p>所有待审核评论都已处理完毕！</p>
    </div>

    <!-- 合并评论列表 -->
    <div v-else class="comments-list">
      <!-- 举报评论（置顶） -->
      <div v-if="reports.length > 0" class="reports-section">
        <h3 class="section-title">🚨 举报评论 ({{ totalReports }})</h3>
        <div 
          v-for="report in reports" 
          :key="'report-' + report.id"
          class="comment-card report-card"
          :class="{ 'selected': selectedComments.includes(report.comment.id) }"
        >
          <div class="comment-header">
            <div class="comment-checkbox">
              <input
                type="checkbox"
                :id="'report-' + report.id"
                :value="report.comment.id"
                v-model="selectedComments"
              />
            </div>
            
            <div class="comment-meta">
              <div class="author-info">
                <span class="username">{{ report.comment.author.username }}</span>
                <span class="role-badge" v-if="report.comment.author.role === 'admin'">管理员</span>
              </div>
              <div class="time-info">
                <span class="report-time">举报时间: {{ formatDate(report.created_at) }}</span>
                <span class="comment-time">评论时间: {{ formatDate(report.comment.created_at) }}</span>
              </div>
            </div>
            
            <div class="report-reason">
              <span class="reason-label">举报原因:</span>
              <span class="reason-text">{{ getReportReasonText(report.reason) }}</span>
              <span v-if="report.custom_reason" class="custom-reason">({{ report.custom_reason }})</span>
            </div>
          </div>

          <div class="comment-content">
            <p>{{ report.comment.content }}</p>
          </div>

          <div class="comment-actions">
            <button 
              class="btn-approve" 
              @click="handleApprove(report.comment.id)"
              :disabled="actionLoading.has(report.comment.id)"
            >
              {{ actionLoading.has(report.comment.id) ? '处理中...' : '恢复显示' }}
            </button>
            <button 
              class="btn-reject" 
              @click="handleReject(report.comment.id)"
              :disabled="actionLoading.has(report.comment.id)"
            >
              {{ actionLoading.has(report.comment.id) ? '处理中...' : '标记违规' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 待审核评论 -->
      <div v-if="pendingComments.length > 0" class="pending-section">
        <h3 class="section-title">⏳ 待审核评论 ({{ totalPending }})</h3>
        <div 
          v-for="comment in pendingComments" 
          :key="'pending-' + comment.id"
          class="comment-card pending-card"
          :class="{ 'selected': selectedComments.includes(comment.id) }"
        >
          <div class="comment-header">
            <div class="comment-checkbox">
              <input
                type="checkbox"
                :id="'pending-' + comment.id"
                :value="comment.id"
                v-model="selectedComments"
              />
            </div>
            
            <div class="comment-meta">
              <div class="author-info">
                <span class="username">{{ comment.author.username }}</span>
                <span class="role-badge" v-if="comment.author.role === 'admin'">管理员</span>
              </div>
              <div class="time-info">
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
            </div>
          </div>

          <div class="comment-content">
            <p>{{ comment.content }}</p>
          </div>

          <div class="comment-actions">
            <button 
              class="btn-approve" 
              @click="handleApprove(comment.id)"
              :disabled="actionLoading.has(comment.id)"
            >
              {{ actionLoading.has(comment.id) ? '处理中...' : '恢复显示' }}
            </button>
            <button 
              class="btn-reject" 
              @click="handleReject(comment.id)"
              :disabled="actionLoading.has(comment.id)"
            >
              {{ actionLoading.has(comment.id) ? '处理中...' : '标记违规' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页器 -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="pagination-btn"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页（共 {{ totalComments }} 条评论）
      </span>
      
      <button 
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="pagination-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useCommentAPI } from '@/composables/useCommentAPI'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

// 权限检查：如果不是管理员，重定向到首页
if (!userStore.isAdmin) {
  alert('您没有权限访问评论管理页面')
  router.push('/')
}

// 状态管理
const filterStatus = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const comments = ref([])
const totalComments = ref(0)
const totalPages = ref(0)
const loading = ref(false)
const batchLoading = ref(false)
const actionLoading = ref(new Set())
const selectedComments = ref([])

// API 调用
const { 
  getAllCommentsAdmin, 
  getPendingComments, 
  auditComment, 
  batchAuditComments,
  getMergedComments
} = useCommentAPI()

// 状态管理 - 更新为支持合并数据
const reports = ref([]) // 举报列表
const pendingComments = ref([]) // 待审核评论
const totalReports = ref(0)
const totalPending = ref(0)

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取举报原因文本
const getReportReasonText = (reason) => {
  const reasonMap = {
    'spam': '垃圾广告',
    'abuse': '人身攻击/辱骂',
    'illegal': '违法违规内容',
    'irrelevant': '与主题无关',
    'other': '其他问题'
  }
  return reasonMap[reason] || reason
}

// 获取评论数据（现在是合并数据）
const fetchComments = async () => {
  loading.value = true
  
  try {
    // 获取合并的评论列表（举报 + 待审核）
    const result = await getMergedComments({
      page: currentPage.value,
      size: pageSize.value
    })
    
    if (result.success) {
      reports.value = result.data.reports
      pendingComments.value = result.data.pendingComments
      totalReports.value = result.data.totalReports
      totalPending.value = result.data.totalPending
      totalPages.value = result.data.totalPages
      
      // 合并到comments用于批量操作（可选）
      comments.value = [...result.data.reports.map(r => r.comment), ...result.data.pendingComments]
      totalComments.value = result.data.totalReports + result.data.totalPending
    } else {
      console.error('Failed to fetch merged comments:', result.message)
      alert(result.message || '获取评论列表失败')
    }
  } catch (err) {
    console.error('fetchComments error:', err)
    alert('获取评论列表时发生错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  fetchComments()
}

// 审核单条评论
const handleApprove = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  
  actionLoading.value.add(commentId)
  
  try {
    const result = await auditComment(commentId, true)
    
    if (result.success) {
      // 更新本地状态
      const commentIndex = comments.value.findIndex(c => c.id === commentId)
      if (commentIndex !== -1) {
        comments.value[commentIndex].is_audited = true
      }
    } else {
      console.error('Failed to approve comment:', result.message)
      alert(result.message || '恢复评论失败')
    }
  } catch (err) {
    console.error('Approve comment error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    actionLoading.value.delete(commentId)
  }
}

const handleReject = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  
  actionLoading.value.add(commentId)
  
  try {
    const result = await auditComment(commentId, false)
    
    if (result.success) {
      // 更新本地状态
      const commentIndex = comments.value.findIndex(c => c.id === commentId)
      if (commentIndex !== -1) {
        comments.value[commentIndex].is_audited = false
      }
    } else {
      console.error('Failed to reject comment:', result.message)
      alert(result.message || '标记违规失败')
    }
  } catch (err) {
    console.error('Reject comment error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    actionLoading.value.delete(commentId)
  }
}

// 批量审核
const handleBatchApprove = async () => {
  if (selectedComments.value.length === 0 || batchLoading.value) return
  
  if (!confirm(`确定要恢复显示 ${selectedComments.value.length} 条评论吗？`)) {
    return
  }
  
  batchLoading.value = true
  
  try {
    const result = await batchAuditComments(selectedComments.value, true)
    
    if (result.success) {
      // 更新本地状态
      comments.value = comments.value.map(comment => {
        if (selectedComments.value.includes(comment.id)) {
          return { ...comment, is_audited: true }
        }
        return comment
      })
      selectedComments.value = []
      alert('批量恢复成功！')
    } else {
      console.error('Failed to batch approve comments:', result.message)
      alert(result.message || '批量恢复失败')
    }
  } catch (err) {
    console.error('Batch approve error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    batchLoading.value = false
  }
}

const handleBatchReject = async () => {
  if (selectedComments.value.length === 0 || batchLoading.value) return
  
  if (!confirm(`确定要标记 ${selectedComments.value.length} 条评论为违规吗？这将隐藏这些评论！`)) {
    return
  }
  
  batchLoading.value = true
  
  try {
    const result = await batchAuditComments(selectedComments.value, false)
    
    if (result.success) {
      // 更新本地状态
      comments.value = comments.value.map(comment => {
        if (selectedComments.value.includes(comment.id)) {
          return { ...comment, is_audited: false }
        }
        return comment
      })
      selectedComments.value = []
      alert('批量标记违规成功！')
    } else {
      console.error('Failed to batch reject comments:', result.message)
      alert(result.message || '批量标记违规失败')
    }
  } catch (err) {
    console.error('Batch reject error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    batchLoading.value = false
  }
}

// 分页导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchComments()
  }
}

// 状态显示辅助函数
const getStatusText = (comment) => {
  if (comment.deleted_at) {
    return '已删除'
  } else if (comment.is_audited === false) {
    return '违规隐藏'
  } else {
    return '正常显示'
  }
}

const getStatusClass = (comment) => {
  if (comment.deleted_at) {
    return 'deleted'
  } else if (comment.is_audited === false) {
    return 'pending'
  } else {
    return 'approved'
  }
}

// 初始化加载
onMounted(() => {
  fetchComments()
})

// 监听分页和筛选变化
watch([currentPage, filterStatus], () => {
  fetchComments()
})
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.comment-admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 32px;
  
  h1 {
    font-size: 2rem;
    font-weight: 700;
    color: $text-main;
    margin: 0 0 8px;
  }
  
  .subtitle {
    font-size: 1.1rem;
    color: $text-secondary;
    margin: 0;
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: $bg-smoke;
  border-radius: 12px;
  
  .filter-section {
    display: flex;
    align-items: center;
    gap: 12px;
    
    label {
      font-weight: 500;
      color: $text-main;
    }
    
    .filter-select {
      padding: 8px 16px;
      border: 1px solid $border-color;
      border-radius: 8px;
      background: white;
      font-size: 1rem;
      cursor: pointer;
      transition: border-color 0.2s ease;
      
      &:hover {
        border-color: $color-primary;
      }
    }
  }
  
  .action-section {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .selection-info {
      color: $text-secondary;
      font-size: 0.95rem;
    }
    
    .btn-batch-approve {
      background: linear-gradient(135deg, $color-success 0%, darken($color-success, 10%) 100%);
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 500;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      box-shadow: 0 4px 12px rgba($color-success, 0.3);
      
      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba($color-success, 0.4);
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }
    }
    
    .btn-batch-reject {
      background: linear-gradient(135deg, $color-danger 0%, darken($color-danger, 10%) 100%);
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 500;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      box-shadow: 0 4px 12px rgba($color-danger, 0.3);
      
      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba($color-danger, 0.4);
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }
    }
  }
}

.loading-state {
  text-align: center;
  padding: 60px 0;
  
  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(0, 0, 0, 0.1);
    border-top: 3px solid $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
  }
  
  p {
    color: $text-secondary;
    font-size: 1.1rem;
  }
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  
  .empty-icon {
    font-size: 4rem;
    margin-bottom: 24px;
    color: $text-secondary;
  }
  
  h3 {
    font-size: 1.5rem;
    color: $text-main;
    margin: 0 0 16px;
  }
  
  p {
    font-size: 1.1rem;
    color: $text-secondary;
    max-width: 500px;
    margin: 0 auto;
  }
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-card {
  background: white;
  border: 1px solid $border-color;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
  
  &.selected {
    border-color: $color-primary;
    background: rgba($color-primary, 0.05);
  }
  
  &.pending {
    border-left: 4px solid $color-warning;
  }
  
  &.deleted {
    opacity: 0.6;
    background: $bg-smoke;
  }
}

.comment-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
  
  .comment-checkbox {
    margin-top: 4px;
    
    input[type="checkbox"] {
      width: 18px;
      height: 18px;
      cursor: pointer;
    }
  }
  
  .comment-meta {
    flex: 1;
    
    .author-info {
      display: flex;
      gap: 12px;
      margin-bottom: 8px;
      flex-wrap: wrap;
      
      .username {
        font-weight: 600;
        color: $text-main;
      }
      
      .article-title {
        color: $text-secondary;
        font-size: 0.9rem;
      }
    }
    
    .time-info {
      display: flex;
      gap: 12px;
      
      .created-at {
        color: $text-secondary;
        font-size: 0.9rem;
      }
      
      .deleted-at {
        color: $color-danger;
        font-size: 0.9rem;
      }
    }
  }
  
  .comment-status {
    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      
      &.pending {
        background: rgba($color-warning, 0.1);
        color: $color-warning;
      }
      
      &.approved {
        background: rgba($color-success, 0.1);
        color: $color-success;
      }
      
      &.deleted {
        background: rgba($color-danger, 0.1);
        color: $color-danger;
      }
    }
  }
}

.comment-content {
  margin-bottom: 16px;
  
  p {
    color: $text-main;
    line-height: 1.6;
    white-space: pre-wrap;
    margin: 0;
  }
}

.comment-actions {
  display: flex;
  gap: 12px;
  
  .btn-approve {
    background: linear-gradient(135deg, $color-success 0%, darken($color-success, 10%) 100%);
    color: white;
    border: none;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba($color-success, 0.3);
    
    &:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba($color-success, 0.4);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
  
  .btn-reject {
    background: linear-gradient(135deg, $color-danger 0%, darken($color-danger, 10%) 100%);
    color: white;
    border: none;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba($color-danger, 0.3);
    
    &:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba($color-danger, 0.4);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid $border-color-light;
  
  .pagination-btn {
    background: white;
    border: 1px solid $border-color;
    color: $text-main;
    padding: 8px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.2s ease;
    
    &:hover:not(:disabled) {
      background: $bg-smoke;
      border-color: $color-primary;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  .page-info {
    color: $text-secondary;
    font-size: 1rem;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}


</style>
<template>
  <div class="report-list-container">
    <div class="page-header">
      <h1>举报管理</h1>
      <p class="subtitle">处理用户举报的不当评论内容</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="reports.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">✅</div>
      <h3>暂无待处理举报</h3>
      <p>所有举报都已处理完毕，感谢您的辛勤工作！</p>
    </div>

    <!-- 举报列表 -->
    <div v-else class="reports-list">
      <div 
        v-for="report in reports" 
        :key="report.id"
        class="report-card"
        :class="{ 'resolved': report.isResolved }"
      >
        <div class="report-header">
          <div class="report-info">
            <span class="report-id">举报 #{{ report.id }}</span>
            <span class="report-time">{{ formatDateTime(report.createdAt) }}</span>
          </div>
          <div class="report-status">
            <span 
              :class="['status-badge', { 'resolved': report.isResolved }]"
            >
              {{ report.isResolved ? '已处理' : '待处理' }}
            </span>
          </div>
        </div>

        <div class="report-content">
          <div class="reported-comment">
            <h4>被举报评论：</h4>
            <div class="comment-preview">
              <div class="comment-author">
                <span class="username">{{ report.comment.author.username }}</span>
                <span class="article-title">在 "{{ report.comment.article?.title || '未知文章' }}" 中评论</span>
              </div>
              <div class="comment-content">
                {{ report.comment.content }}
              </div>
            </div>
          </div>

          <div class="report-reason">
            <h4>举报原因：</h4>
            <p>{{ report.reason }}</p>
          </div>

          <div class="reporter-info">
            <h4>举报人：</h4>
            <span class="reporter-username">{{ report.reporter.username }}</span>
          </div>
        </div>

        <div class="report-actions" v-if="!report.isResolved">
          <button 
            class="btn-resolve" 
            @click="handleResolveReport(report.id)"
            :disabled="resolvingIds.has(report.id)"
          >
            {{ resolvingIds.has(report.id) ? '处理中...' : '标记为已处理' }}
          </button>
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
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
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
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import * as commentService from '@/services/commentService'
import { formatDateTime } from '@/utils'

const userStore = useUserStore()
const router = useRouter()

// 权限检查：如果不是管理员，重定向到首页
if (!userStore.isAdmin) {
  alert('您没有权限访问举报管理页面')
  router.push('/')
}

// 分页和数据状态
const currentPage = ref(1)
const pageSize = ref(10)
const reports = ref([])
const totalReports = ref(0)
const totalPages = ref(0)
const loading = ref(false)
const resolvingIds = ref(new Set())

// API 调用
// 格式化日期 - 使用 utils 中的 formatDateTime

// 获取举报列表
const fetchReports = async () => {
  loading.value = true
  
  try {
    const result = await commentService.getAdminReports({
      page: currentPage.value,
      size: pageSize.value
    })
    
    if (result.success) {
      reports.value = result.data.items
      totalReports.value = result.data.total
      totalPages.value = result.data.pages
    } else {
      console.error('Failed to fetch reports:', result.message)
      alert(result.message || '获取举报列表失败')
    }
  } catch (err) {
    console.error('Fetch reports error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理举报（标记为已处理）
const handleResolveReport = async (reportId) => {
  if (resolvingIds.value.has(reportId)) return
  
  resolvingIds.value.add(reportId)
  
  try {
    const result = await commentService.resolveReport(reportId)
    
    if (result.success) {
      // 更新本地状态
      const reportIndex = reports.value.findIndex(r => r.id === reportId)
      if (reportIndex !== -1) {
        reports.value[reportIndex].isResolved = true
      }
    } else {
      console.error('Failed to resolve report:', result.message)
      alert(result.message || '处理举报失败')
    }
  } catch (err) {
    console.error('Resolve report error:', err)
    alert('网络错误，请稍后重试')
  } finally {
    resolvingIds.value.delete(reportId)
  }
}

// 分页导航
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchReports()
  }
}

// 初始化加载
onMounted(() => {
  fetchReports()
})

// 监听分页变化
// 注意：这里简化了实现，实际项目中可能需要更复杂的分页逻辑
</script>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.report-list-container {
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
    color: $color-success;
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

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-card {
  background: white;
  border: 1px solid $border-color;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.2s ease;
  
  &:hover:not(.resolved) {
    border-color: $color-primary;
    box-shadow: 0 4px 12px rgba($color-primary, 0.1);
  }
  
  &.resolved {
    opacity: 0.7;
    background: $bg-smoke;
  }
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid $border-color-light;
  
  .report-info {
    display: flex;
    gap: 16px;
    
    .report-id {
      font-weight: 600;
      color: $text-main;
    }
    
    .report-time {
      color: $text-secondary;
      font-size: 0.9rem;
    }
  }
  
  .report-status {
    .status-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      
      &.resolved {
        background: rgba($color-success, 0.1);
        color: $color-success;
      }
      
      &:not(.resolved) {
        background: rgba($color-warning, 0.1);
        color: $color-warning;
      }
    }
  }
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.reported-comment {
  h4 {
    margin: 0 0 12px;
    color: $text-main;
    font-size: 1.1rem;
  }
  
  .comment-preview {
    background: $bg-smoke;
    border-radius: 12px;
    padding: 16px;
    
    .comment-author {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;
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
    
    .comment-content {
      color: $text-main;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}

.report-reason {
  h4 {
    margin: 0 0 12px;
    color: $text-main;
    font-size: 1.1rem;
  }
  
  p {
    background: rgba($color-warning, 0.05);
    border-left: 4px solid $color-warning;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    color: $text-main;
    line-height: 1.5;
  }
}

.reporter-info {
  h4 {
    margin: 0 0 8px;
    color: $text-main;
    font-size: 1.1rem;
  }
  
  .reporter-username {
    background: rgba($color-primary, 0.05);
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 500;
    color: $color-primary;
  }
}

.report-actions {
  margin-top: 24px;
  text-align: right;
  
  .btn-resolve {
    background: linear-gradient(135deg, $color-success 0%, darken($color-success, 10%) 100%);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
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
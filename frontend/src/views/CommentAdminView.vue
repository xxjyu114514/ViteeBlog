<template>
  <div class="comment-admin-container">
    <div class="page-header">
      <h1>评论巡查</h1>
      <p class="subtitle">全站评论管理与审核</p>
    </div>

    <div class="toolbar">
      <div class="filter-section">
        <label for="status-filter">状态筛选：</label>
        <select id="status-filter" v-model="filterStatus" @change="handleFilterChange" class="filter-select">
          <option value="all">全部评论</option>
          <option value="pending">违规评论</option>
          <option value="approved">正常评论</option>
          <option value="deleted">已删除评论</option>
        </select>
      </div>

      <div class="action-section" v-if="selectedCommentIds.length > 0">
        <span class="selection-info">已选择 {{ selectedCommentIds.length }} 条评论</span>
        <button class="btn-batch-approve" @click="handleBatchApprove" :disabled="batchLoading">
          {{ batchLoading ? '处理中...' : '批量恢复显示' }}
        </button>
        <button class="btn-batch-reject" @click="handleBatchReject" :disabled="batchLoading">
          {{ batchLoading ? '处理中...' : '批量标记违规' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="!reports.length && !pendingComments.length" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>暂无待审核评论</h3>
      <p>所有待审核评论都已处理完毕！</p>
    </div>

    <div v-else class="comments-list">
      <div v-if="reports.length > 0" class="section">
        <h3 class="section-title">🚨 举报评论 ({{ totalReports }})</h3>
        <CommentReviewCard
          v-for="report in reports"
          :key="'report-' + report.id"
          :comment="report.comment"
          type="report"
          :report-data="report"
          :selected="selectedCommentIds.includes(report.comment.id)"
          :loading="actionLoading.has(report.comment.id)"
          @update:selected="(v) => toggleSelect(report.comment.id, v)"
          @approve="handleApprove"
          @reject="handleReject"
        />
      </div>

      <div v-if="pendingComments.length > 0" class="section">
        <h3 class="section-title">⏳ 待审核评论 ({{ totalPending }})</h3>
        <CommentReviewCard
          v-for="comment in pendingComments"
          :key="'pending-' + comment.id"
          :comment="comment"
          type="pending"
          :selected="selectedCommentIds.includes(comment.id)"
          :loading="actionLoading.has(comment.id)"
          @update:selected="(v) => toggleSelect(comment.id, v)"
          @approve="handleApprove"
          @reject="handleReject"
        />
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)" class="pagination-btn">上一页</button>
      <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页（共 {{ totalComments }} 条评论）</span>
      <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)" class="pagination-btn">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import * as commentService from '@/services/commentService'
import CommentReviewCard from '@/components/CommentReviewCard.vue'

const userStore = useUserStore()
const router = useRouter()

if (!userStore.isAdmin) {
  alert('您没有权限访问评论管理页面')
  router.push('/')
}

const filterStatus = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const totalComments = ref(0)
const totalPages = ref(0)
const loading = ref(false)
const batchLoading = ref(false)
const actionLoading = ref(new Set())
const selectedCommentIds = ref([])

const reports = ref([])
const pendingComments = ref([])
const totalReports = ref(0)
const totalPending = ref(0)

const fetchComments = async () => {
  loading.value = true
  try {
    const result = await commentService.getMergedComments({ page: currentPage.value, size: pageSize.value })
    if (result.success) {
      reports.value = result.data.reports || []
      pendingComments.value = result.data.pendingComments || []
      totalReports.value = result.data.totalReports || 0
      totalPending.value = result.data.totalPending || 0
      totalPages.value = result.data.totalPages || 0
      totalComments.value = totalReports.value + totalPending.value
    } else {
      alert(result.message || '获取评论列表失败')
    }
  } catch (err) {
    alert('获取评论列表时发生错误，请稍后重试')
  }
  loading.value = false
}

const toggleSelect = (id, checked) => {
  if (checked) {
    if (!selectedCommentIds.value.includes(id)) selectedCommentIds.value.push(id)
  } else {
    selectedCommentIds.value = selectedCommentIds.value.filter(i => i !== id)
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchComments()
}

const handleApprove = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  actionLoading.value.add(commentId)
  const result = await commentService.auditComment(commentId, true)
  if (!result.success) alert(result.message || '恢复评论失败')
  actionLoading.value.delete(commentId)
}

const handleReject = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  actionLoading.value.add(commentId)
  const result = await commentService.auditComment(commentId, false)
  if (!result.success) alert(result.message || '标记违规失败')
  actionLoading.value.delete(commentId)
}

const handleBatchApprove = async () => {
  if (!selectedCommentIds.value.length || batchLoading.value) return
  if (!confirm(`确定要恢复显示 ${selectedCommentIds.value.length} 条评论吗？`)) return
  batchLoading.value = true
  const result = await commentService.batchAuditComments(selectedCommentIds.value, true)
  if (result.success) {
    selectedCommentIds.value = []
    alert('批量恢复成功！')
  } else {
    alert(result.message || '批量恢复失败')
  }
  batchLoading.value = false
}

const handleBatchReject = async () => {
  if (!selectedCommentIds.value.length || batchLoading.value) return
  if (!confirm(`确定要标记 ${selectedCommentIds.value.length} 条评论为违规吗？`)) return
  batchLoading.value = true
  const result = await commentService.batchAuditComments(selectedCommentIds.value, false)
  if (result.success) {
    selectedCommentIds.value = []
    alert('批量标记违规成功！')
  } else {
    alert(result.message || '批量标记违规失败')
  }
  batchLoading.value = false
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchComments()
  }
}

onMounted(() => fetchComments())
watch([currentPage, filterStatus], () => fetchComments())
</script>

<style scoped lang="scss">
@use 'sass:color';
@use '@/assets/styles/variables' as *;

.comment-admin-container { max-width: 1200px; margin: 0 auto; padding: 20px; }

.page-header {
  margin-bottom: 32px;
  h1 { font-size: 2rem; font-weight: 700; color: $text-main; margin: 0 0 8px; }
  .subtitle { font-size: 1.1rem; color: $text-secondary; margin: 0; }
}

.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px; padding: 16px; background: $bg-smoke; border-radius: 12px;
  .filter-section {
    display: flex; align-items: center; gap: 12px;
    label { font-weight: 500; color: $text-main; }
    .filter-select {
      padding: 8px 16px; border: 1px solid $border-color; border-radius: 8px;
      background: $bg-surface; font-size: 1rem; cursor: pointer;
      &:hover { border-color: $color-primary; }
    }
  }
  .action-section {
    display: flex; align-items: center; gap: 16px;
    .selection-info { color: $text-secondary; font-size: 0.95rem; }
    .btn-batch-approve, .btn-batch-reject {
      border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer;
      font-size: 0.95rem; font-weight: 500; color: $bg-base;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      &:hover:not(:disabled) { transform: translateY(-2px); }
      &:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
    }
    .btn-batch-approve {
      background: linear-gradient(135deg, $color-success 0%, color.adjust($color-success, $lightness: -10%) 100%);
      box-shadow: 0 4px 12px rgba($color-success, 0.3);
      &:hover:not(:disabled) { box-shadow: 0 6px 16px rgba($color-success, 0.4); }
    }
    .btn-batch-reject {
      background: linear-gradient(135deg, $color-danger 0%, color.adjust($color-danger, $lightness: -10%) 100%);
      box-shadow: 0 4px 12px rgba($color-danger, 0.3);
      &:hover:not(:disabled) { box-shadow: 0 6px 16px rgba($color-danger, 0.4); }
    }
  }
}

.loading-state {
  text-align: center; padding: 60px 0;
  .spinner {
    width: 32px; height: 32px; border: 3px solid rgba(255, 255, 255, 0.08);
    border-top: 3px solid $color-primary; border-radius: 50%;
    animation: spin 1s linear infinite; margin: 0 auto 16px;
  }
  p { color: $text-secondary; font-size: 1.1rem; }
}

.empty-state { text-align: center; padding: 80px 0; }

.section { margin-bottom: 24px; }
.section-title { font-size: 1.2rem; font-weight: 600; color: $text-main; margin: 0 0 16px; }

.comments-list { display: flex; flex-direction: column; gap: 16px; }

.pagination {
  display: flex; justify-content: center; align-items: center; gap: 24px;
  margin-top: 40px; padding-top: 24px; border-top: 1px solid $border-color-light;
  .pagination-btn {
    background: $bg-surface; border: $border-white-light; color: $text-main;
    padding: 8px 20px; cursor: pointer; font-size: 1rem;
    transition: all 0.2s ease;
    &:hover:not(:disabled) { background: $bg-smoke; border-color: $color-primary; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
  .page-info { color: $text-secondary; font-size: 1rem; }
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>

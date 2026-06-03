<template>
  <div class="comment-admin-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <button class="btn-back" @click="router.push('/admin-dashboard')">← 返回</button>
          <span class="card-title">评论巡查</span>
        </div>
        <div class="card-body">
          <div class="toolbar">
            <div class="filter-section">
              <label>状态筛选：</label>
              <select v-model="filterStatus" @change="handleFilterChange" class="filter-select">
                <option value="all">全部评论</option>
                <option value="pending">违规评论</option>
                <option value="approved">正常评论</option>
                <option value="deleted">已删除评论</option>
              </select>
            </div>
            <div class="action-section" v-if="selectedCommentIds.length > 0">
              <span class="selection-info">已选择 {{ selectedCommentIds.length }} 条</span>
              <button class="btn-batch-approve" @click="handleBatchApprove" :disabled="batchLoading">{{ batchLoading ? '处理中...' : '批量恢复' }}</button>
              <button class="btn-batch-reject" @click="handleBatchReject" :disabled="batchLoading">{{ batchLoading ? '处理中...' : '批量标记违规' }}</button>
            </div>
          </div>

          <div v-if="loading" class="state-msg"><div class="spinner"></div><p>加载中...</p></div>
          <div v-else-if="!reports.length && !pendingComments.length" class="state-msg"><p>暂无待处理评论</p></div>
          <div v-else class="comments-list">
            <div v-if="reports.length > 0" class="section">
              <h3 class="section-title">🚨 举报评论 ({{ totalReports }})</h3>
              <CommentReviewCard v-for="report in reports" :key="'report-' + report.id" :comment="report.comment" type="report" :report-data="report" :selected="selectedCommentIds.includes(report.comment.id)" :loading="actionLoading.has(report.comment.id)" @update:selected="(v) => toggleSelect(report.comment.id, v)" @approve="handleApprove" @reject="handleReject" />
            </div>
            <div v-if="pendingComments.length > 0" class="section">
              <h3 class="section-title">⏳ 待审核评论 ({{ totalPending }})</h3>
              <CommentReviewCard v-for="comment in pendingComments" :key="'pending-' + comment.id" :comment="comment" type="pending" :selected="selectedCommentIds.includes(comment.id)" :loading="actionLoading.has(comment.id)" @update:selected="(v) => toggleSelect(comment.id, v)" @approve="handleApprove" @reject="handleReject" />
            </div>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)" class="page-btn">上一页</button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)" class="page-btn">下一页</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as commentService from '@/services/commentService'
import CommentReviewCard from '@/components/CommentReviewCard.vue'

const router = useRouter()
const slidIn = ref(false)
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
  const result = await commentService.getMergedComments({ page: currentPage.value, size: pageSize.value })
  if (result.success) {
    reports.value = result.data.reports || []
    pendingComments.value = result.data.pendingComments || []
    totalReports.value = result.data.totalReports || 0
    totalPending.value = result.data.totalPending || 0
    totalPages.value = result.data.totalPages || 0
    totalComments.value = totalReports.value + totalPending.value
  }
  loading.value = false
}

const toggleSelect = (id, checked) => {
  if (checked) { if (!selectedCommentIds.value.includes(id)) selectedCommentIds.value.push(id) }
  else { selectedCommentIds.value = selectedCommentIds.value.filter(i => i !== id) }
}

const handleFilterChange = () => { currentPage.value = 1; fetchComments() }

const handleApprove = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  actionLoading.value.add(commentId)
  const r = await commentService.auditComment(commentId, true)
  if (!r.success) alert(r.message || '恢复失败')
  actionLoading.value.delete(commentId)
}

const handleReject = async (commentId) => {
  if (actionLoading.value.has(commentId)) return
  actionLoading.value.add(commentId)
  const r = await commentService.auditComment(commentId, false)
  if (!r.success) alert(r.message || '标记失败')
  actionLoading.value.delete(commentId)
}

const handleBatchApprove = async () => {
  if (!selectedCommentIds.value.length || batchLoading.value) return
  if (!confirm(`恢复显示 ${selectedCommentIds.value.length} 条？`)) return
  batchLoading.value = true
  const r = await commentService.batchAuditComments(selectedCommentIds.value, true)
  if (r.success) { selectedCommentIds.value = []; alert('批量恢复成功！') }
  else alert(r.message || '批量恢复失败')
  batchLoading.value = false
}

const handleBatchReject = async () => {
  if (!selectedCommentIds.value.length || batchLoading.value) return
  if (!confirm(`标记 ${selectedCommentIds.value.length} 条为违规？`)) return
  batchLoading.value = true
  const r = await commentService.batchAuditComments(selectedCommentIds.value, false)
  if (r.success) { selectedCommentIds.value = []; alert('批量标记成功！') }
  else alert(r.message || '批量标记失败')
  batchLoading.value = false
}

const goToPage = (page) => { if (page >= 1 && page <= totalPages.value) currentPage.value = page }

onMounted(() => { fetchComments(); requestAnimationFrame(() => { slidIn.value = true }) })
watch([currentPage, filterStatus], () => fetchComments())
</script>

<style lang="scss">
@use 'sass:color';
@use './test_scss.scss' as *;

.comment-admin-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

.glass-wrap {
  position: absolute; bottom: 0; left: $space-lg; right: $space-lg;
  height: calc(100vh - 90px - 5vh); display: flex; flex-direction: column;
}

.glass-card {
  background: rgba(26, 26, 31, 0.92);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid $glass-border; border-bottom: none;
  display: flex; flex-direction: column; height: 100%;
  transform: translateY(100%);
  opacity: 0;
  transition: transform 0.45s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.4s ease;
  overflow: hidden;
  &.slide-in { transform: translateY(0); opacity: 1; }
}

.card-header {
  display: flex; align-items: center; gap: $space-md;
  padding: $space-md $space-xl;
  border-bottom: 1px solid $glass-border; flex-shrink: 0;
  .btn-back { background: none; border: none; color: $text-secondary; cursor: pointer; font-size: 0.9rem; padding: 0; &:hover { color: $text-primary; } }
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: $space-lg; padding: $space-md; background: $bg-surface; border: 1px solid $glass-border;
  .filter-section { display: flex; align-items: center; gap: $space-sm; label { font-size: 0.85rem; color: $text-secondary; } }
  .filter-select { padding: 6px 12px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-primary; font-size: 0.85rem; &:focus { outline: none; border-color: $color-primary; } }
  .action-section { display: flex; align-items: center; gap: $space-sm; }
  .selection-info { font-size: 0.85rem; color: $text-secondary; }
}

.btn-batch-approve, .btn-batch-reject {
  padding: 6px 14px; border: none; cursor: pointer; font-size: 0.8rem; font-weight: 500; color: $bg-base;
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}
.btn-batch-approve { background: $color-success; &:hover { background: color.adjust($color-success, $lightness: 6%); } }
.btn-batch-reject { background: $color-error; &:hover { background: color.adjust($color-error, $lightness: 6%); } }

.state-msg { text-align: center; padding: 60px 0; p { color: $text-secondary; } }
.spinner { width: 24px; height: 24px; border: 2px solid rgba($text-tertiary, 0.25); border-top-color: $color-primary; border-radius: 50%; animation: mspin 0.8s linear infinite; margin: 0 auto 12px; }
@keyframes mspin { to { transform: rotate(360deg); } }

.section { margin-bottom: $space-lg; }
.section-title { font-size: 1rem; font-weight: 600; color: $text-primary; margin: 0 0 $space-md; }
.comments-list { display: flex; flex-direction: column; gap: $space-md; }

.pagination { display: flex; justify-content: center; align-items: center; gap: $space-md; margin-top: $space-xl; padding-top: $space-md; border-top: 1px solid $glass-border; }
.page-btn { padding: 6px 16px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-secondary; cursor: pointer; font-size: 0.85rem; &:hover { color: $text-primary; border-color: $color-primary; } &:disabled { opacity: 0.4; cursor: not-allowed; } }
.page-info { font-size: 0.8rem; color: $text-tertiary; }
</style>

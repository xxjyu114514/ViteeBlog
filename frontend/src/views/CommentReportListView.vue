<template>
  <div class="report-page">
    <div class="glass-wrap">
      <div class="glass-card" :class="{ 'slide-in': slidIn }">
        <div class="card-header">
          <span class="card-title">举报管理</span>
        </div>
        <div class="card-body">
          <div v-if="loading" class="state-msg"><div class="spinner"></div><p>加载中...</p></div>
          <div v-else-if="reports.length === 0" class="state-msg"><p>暂无待处理举报</p></div>
          <div v-else class="reports-list">
            <div v-for="report in reports" :key="report.id" class="report-item" :class="{ resolved: report.isResolved }">
              <div class="report-head">
                <div class="report-head-info">
                  <span class="report-id">#{{ report.id }}</span>
                  <span class="report-time">{{ formatDateTime(report.createdAt) }}</span>
                  <span :class="['report-status', report.isResolved ? 'done' : 'pending']">{{ report.isResolved ? '已处理' : '待处理' }}</span>
                </div>
              </div>
              <div class="report-detail">
                <div class="detail-row">
                  <span class="detail-label">被举报评论：</span>
                  <div class="detail-comment">
                    <span class="comment-author">{{ report.comment?.author?.username || '匿名' }}</span>
                    <p class="comment-text">{{ report.comment?.content }}</p>
                  </div>
                </div>
                <div class="detail-row">
                  <span class="detail-label">举报原因：</span>
                  <p class="detail-reason">{{ report.reason }}</p>
                </div>
                <div class="detail-row">
                  <span class="detail-label">举报人：</span>
                  <span class="detail-reporter">{{ report.reporter?.username }}</span>
                </div>
              </div>
              <div v-if="!report.isResolved" class="report-actions">
                <label class="hide-label">
                  <input type="checkbox" :checked="hideCommentIds.includes(report.comment?.id)" @change="toggleHideId(report.comment?.id)" />
                  同时隐藏评论
                </label>
                <button class="btn-resolve" @click="handleResolveReport(report.id, report.comment?.id)" :disabled="resolvingIds.has(report.id)">{{ resolvingIds.has(report.id) ? '处理中...' : '标记已处理' }}</button>
              </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as commentService from '@/services/commentService'
import { formatDateTime } from '@/utils'

const router = useRouter()
const slidIn = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const reports = ref([])
const totalReports = ref(0)
const totalPages = ref(0)
const loading = ref(false)
const resolvingIds = ref(new Set())
const hideCommentIds = ref([])

const toggleHideId = (id) => {
  if (!id) return
  if (hideCommentIds.value.includes(id)) hideCommentIds.value = hideCommentIds.value.filter(i => i !== id)
  else hideCommentIds.value.push(id)
}

const fetchReports = async () => {
  loading.value = true
  const result = await commentService.getAdminReports({ page: currentPage.value, size: pageSize.value })
  if (result.success) {
    reports.value = result.data.items || []
    totalReports.value = result.data.total || 0
    totalPages.value = result.data.pages || 0
  }
  loading.value = false
}

const handleResolveReport = async (reportId, commentId) => {
  if (resolvingIds.value.has(reportId)) return
  resolvingIds.value.add(reportId)
  const result = await commentService.resolveReport(reportId)
  if (result.success) {
    if (hideCommentIds.value.includes(commentId)) {
      await commentService.auditComment(commentId, false)
      hideCommentIds.value = hideCommentIds.value.filter(id => id !== commentId)
    }
    const idx = reports.value.findIndex(r => r.id === reportId)
    if (idx !== -1) reports.value[idx].isResolved = true
  }
  resolvingIds.value.delete(reportId)
}

const goToPage = (page) => { if (page >= 1 && page <= totalPages.value) { currentPage.value = page; fetchReports() } }

onMounted(() => { fetchReports(); requestAnimationFrame(() => { slidIn.value = true }) })
</script>

<style lang="scss">
@use 'sass:color';
@use './_design.scss' as *;

.report-page { position: fixed; inset: 0; z-index: 1; overflow: hidden; }

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
  // .btn-back 5df2572851685c40 views.scss 4e2d5b9a4e49
  .card-title { font-family: $font-mono; font-size: 1rem; font-weight: 600; color: $text-primary; }
}

.card-body { flex: 1; overflow-y: auto; padding: $space-xl; }

.state-msg { text-align: center; padding: 60px 0; p { color: $text-secondary; } }
.spinner { width: 24px; height: 24px; border: 2px solid rgba($text-tertiary, 0.25); border-top-color: $color-primary; border-radius: 50%; animation: mspin 0.8s linear infinite; margin: 0 auto 12px; }
@keyframes mspin { to { transform: rotate(360deg); } }

.reports-list { display: flex; flex-direction: column; gap: $space-md; }

.report-item {
  padding: $space-lg; background: $bg-surface; border: 1px solid $glass-border;
  transition: border-color 0.2s;
  &:hover { border-color: $glass-border-hover; }
  &.resolved { opacity: 0.6; }
}

.report-head { margin-bottom: $space-md; padding-bottom: $space-sm; border-bottom: 1px solid $divider-hairline; }
.report-head-info { display: flex; gap: $space-md; align-items: center; font-size: 0.9rem; }
.report-id { font-weight: 600; color: $text-primary; }
.report-time { color: $text-tertiary; font-size: 0.8rem; }
.report-status { padding: 2px 8px; font-size: 0.75rem; font-weight: 500; }
.report-status.pending { background: rgba($color-warning, 0.12); color: $color-warning; }
.report-status.done { background: rgba($color-success, 0.12); color: $color-success; }

.report-detail { display: flex; flex-direction: column; gap: $space-md; }
.detail-row { display: flex; gap: $space-sm; }
.detail-label { font-size: 0.85rem; color: $text-secondary; white-space: nowrap; padding-top: 2px; min-width: 80px; }
.detail-comment { flex: 1; }
.comment-author { font-size: 0.85rem; font-weight: 600; color: $text-primary; }
.comment-text { font-size: 0.85rem; color: $text-secondary; margin-top: 4px; line-height: 1.5; white-space: pre-wrap; }
.detail-reason { flex: 1; font-size: 0.85rem; color: $text-primary; padding: 6px 10px; background: $bg-elevated; }
.detail-reporter { font-size: 0.85rem; color: $color-primary; }

.report-actions { display: flex; justify-content: flex-end; align-items: center; gap: $space-md; margin-top: $space-md; padding-top: $space-md; border-top: 1px solid $divider-hairline; }
.hide-label { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; color: $text-secondary; cursor: pointer; input { width: 14px; height: 14px; cursor: pointer; } }

.btn-resolve {
  padding: 6px 18px; border: none; background: $color-success; color: $bg-base;
  font-size: 0.85rem; cursor: pointer; font-weight: 500;
  &:hover { background: color.adjust($color-success, $lightness: 6%); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
}

.pagination { display: flex; justify-content: center; align-items: center; gap: $space-md; margin-top: $space-xl; padding-top: $space-md; border-top: 1px solid $glass-border; }
.page-btn { padding: 6px 16px; background: $bg-elevated; border: 1px solid $glass-border; color: $text-secondary; cursor: pointer; font-size: 0.85rem; &:hover { color: $text-primary; border-color: $color-primary; } &:disabled { opacity: 0.4; cursor: not-allowed; } }
.page-info { font-size: 0.8rem; color: $text-tertiary; }
</style>

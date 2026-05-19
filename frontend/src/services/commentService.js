/**
 * 评论服务 — /api/v1/comments/*
 * 所有函数返回 ApiResponse 格式
 */
import { get, post, put, del } from '@/api/client'

/** POST /comments/articles/{articleId}/comments */
export const createComment = (articleId, commentData) =>
  post(`/comments/articles/${articleId}/comments`, commentData)

/** GET /comments/articles/{articleId}/comments */
export const getCommentsByArticle = (articleId, params = {}) =>
  get(`/comments/articles/${articleId}/comments`, params)

/** DELETE /comments/{commentId} */
export const deleteComment = (commentId) =>
  del(`/comments/${commentId}`)

/** POST /comments/{commentId}/like */
export const likeComment = (commentId) =>
  post(`/comments/${commentId}/like`, {})

/** POST /comments/{commentId}/report */
export const reportComment = (commentId, reason) =>
  post(`/comments/${commentId}/report`, { reason })

/** GET /comments/admin/reports */
export const getAdminReports = (params = {}) =>
  get('/comments/admin/reports', params)

/** PUT /comments/admin/reports/{reportId}/resolve */
export const resolveReport = (reportId) =>
  put(`/comments/admin/reports/${reportId}/resolve`, {})

/** GET /comments/admin/comments/all */
export const getAllCommentsAdmin = (params = {}) =>
  get('/comments/admin/comments/all', params)

/** GET /comments/admin/comments/pending */
export const getPendingComments = (params = {}) =>
  get('/comments/admin/comments/pending', params)

/** PUT /comments/admin/comments/{commentId}/audit */
export const auditComment = (commentId, passAudit) =>
  put(`/comments/admin/comments/${commentId}/audit`, { pass_audit: passAudit })

/** POST /comments/admin/comments/batch-audit */
export const batchAuditComments = (commentIds, passAudit) =>
  post('/comments/admin/comments/batch-audit', { comment_ids: commentIds, pass_audit: passAudit })

/**
 * 获取合并的巡查数据（举报 + 待审核评论）
 * 前端合并两个 API 调用，后端暂未提供统一端点
 */
export const getMergedComments = async (params = {}) => {
  const [reportsRes, pendingRes] = await Promise.all([
    get('/comments/admin/reports', params),
    get('/comments/admin/comments/pending', params),
  ])
  return {
    success: reportsRes.success && pendingRes.success,
    data: {
      reports: reportsRes.data?.items || [],
      pendingComments: pendingRes.data?.items || [],
      totalReports: reportsRes.data?.total || 0,
      totalPending: pendingRes.data?.total || 0,
      totalPages: Math.max(reportsRes.data?.pages || 0, pendingRes.data?.pages || 0),
    },
  }
}

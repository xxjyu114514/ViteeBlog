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

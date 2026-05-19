import { ref } from 'vue'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useCommentAPI() {
  // 评论操作的loading状态
  const commentLoading = ref(false)
  // 防重复提交锁
  const commentSubmitLock = ref(false)
  
  // 获取文章评论列表
  const getCommentsByArticle = async (articleId, params = {}) => {
    commentLoading.value = true
    
    try {
      const url = buildUrl('/comments/articles/:article_id/comments', { article_id: articleId }, params)
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取评论') }
      }

            // 后端返回分页对象格式：{ items: [...], total: number, page: number, size: number, pages: number }
      const responseData = data.value || {}
      
      const safeData = {
        items: Array  .isArray(responseData.items) ? responseData.items : [],
        total: responseData.total || 0,
        page: responseData.page || 1,
        size: responseData.size || 20,
        pages: responseData.pages || 0
      }

      return { success: true, data: safeData }
    } catch (err) {
      console.error('getCommentsByArticle error:', err)
      return { success: false, message: '获取评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
    }
  }

  // 创建评论
  const createComment = async (commentData, articleId) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '评论正在提交中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/articles/:article_id/comments', { article_id: articleId })
      const { data, error } = await useBaseFetch(url).post(commentData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '发表评论') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('createComment error:', err)
      return { success: false, message: '发表评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 点赞/取消点赞评论
  const likeComment = async (commentId) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/:comment_id/like', { comment_id: commentId })
      const { data, error } = await useBaseFetch(url).post({}).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '点赞操作') }
      }
      
      return { 
        success: true,
        data: {
          is_liked: data.value.liked,
          like_count: data.value.like_count
        }
      }
    } catch (err) {
      console.error('toggleCommentLike error:', err)
      return { success: false, message: '点赞操作时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 举报评论
  const reportComment = async (commentId, reason) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '举报正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/:comment_id/report', { comment_id: commentId })
      const { data, error } = await useBaseFetch(url).post({ reason }).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '举报评论') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('reportComment error:', err)
      return { success: false, message: '举报评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 管理员：获取待处理举报列表
  const getAdminReports = async (params = {}) => {
    // 移除 commentSubmitLock 检查，因为这是数据获取而非提交操作
    commentLoading.value = true
    // 不设置 commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/admin/reports', {}, params)
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取举报列表') }
      }
      
      // 后端返回分页对象格式
      const safeData = {
        items: Array.isArray(data.value?.items) ? data.value.items : [],
        total: data.value?.total || 0,
        page: data.value?.page || 1,
        size: data.value?.size || 20,
        pages: data.value?.pages || 0
      }

      return { success: true, data: safeData }
    } catch (err) {
      console.error('getAdminReports error:', err)
      return { success: false, message: '获取举报列表时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      // 不修改 commentSubmitLock
    }
  }

  // 管理员：处理举报（标记为已处理）
  const resolveReport = async (reportId) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/admin/reports/:report_id/resolve', { report_id: reportId })
      const { data, error } = await useBaseFetch(url).put({ status }).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '处理举报') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('resolveReport error:', err)
      return { success: false, message: '处理举报时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 管理员：获取全站评论（包括已删除的）
  const getAllCommentsAdmin = async (params = {}) => {
    // 移除 commentSubmitLock 检查，因为这是数据获取而非提交操作
    commentLoading.value = true
    // 不设置 commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/admin/comments/all', {}, params)
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取全站评论') }
      }
      
      // 后端返回分页对象格式
      const safeData = {
        items: Array.isArray(data.value?.items) ? data.value.items : [],
        total: data.value?.total || 0,
        page: data.value?.page || 1,
        size: data.value?.size || 20,
        pages: data.value?.pages || 0
      }

      return { success: true, data: safeData }
    } catch (err) {
      console.error('getAllCommentsAdmin error:', err)
      return { success: false, message: '获取全站评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      // 不修改 commentSubmitLock
    }
  }

  // 管理员：获取违规评论列表（is_audited = false）
  const getPendingComments = async (params = {}) => {
    commentLoading.value = true
    // 不使用commentSubmitLock，因为这是数据获取而非提交操作
    
    try {
      const url = buildUrl('/comments/admin/comments/pending', {}, params)
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取违规评论') }
      }
      
      // 后端返回分页对象格式
      const safeData = {
        items: Array.isArray(data.value?.items) ? data.value.items : [],
        total: data.value?.total || 0,
        page: data.value?.page || 1,
        size: data.value?.size || 20,
        pages: data.value?.pages || 0
      }
      
      return { success: true, data: safeData }
    } catch (err) {
      console.error('getPendingComments error:', err)
      return { success: false, message: '获取违规评论失败，请稍后重试' }
    } finally {
      commentLoading.value = false
      // 不修改 commentSubmitLock
    }
  }

  // 管理员：审核单条评论（标记违规或恢复显示）
  const auditComment = async (commentId, passAudit) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/admin/comments/:comment_id/audit', { comment_id: commentId })
      const { data, error } = await useBaseFetch(url).put({ action }).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '审核评论') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('auditComment error:', err)
      return { success: false, message: '审核评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 批量审核评论（管理员）
  const batchAuditComments = async (commentIds, action) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/admin/comments/batch-audit')
      const { data, error } = await useBaseFetch(url).put({ comment_ids: commentIds, action }).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '批量审核') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('batchAuditComments error:', err)
      return { success: false, message: '批量审核失败，请稍后重试' }
    } finally {
      commentSubmitLock.value = false
      commentLoading.value = false
    }
  }

  // 新增：获取合并的评论列表（举报 + 待审核）
  const getMergedComments = async (params = {}) => {
    commentLoading.value = true
    // 不使用commentSubmitLock，因为这是数据获取而非提交操作
    
    try {
      // 并行获取举报列表和待审核评论
      const [reportsResult, pendingResult] = await Promise.all([
        getAdminReports(params),
        getPendingComments(params)
      ])
      
      if (!reportsResult.success && !pendingResult.success) {
        return { 
          success: false, 
          message: `获取数据失败：${reportsResult.message || ''} ${pendingResult.message || ''}`.trim() 
        }
      }
      
      // 合并数据
      const mergedData = {
        reports: reportsResult.success ? reportsResult.data.items : [],
        pendingComments: pendingResult.success ? pendingResult.data.items : [],
        totalReports: reportsResult.success ? reportsResult.data.total : 0,
        totalPending: pendingResult.success ? pendingResult.data.total : 0,
        totalPages: Math.max(
          reportsResult.success ? reportsResult.data.pages : 0,
          pendingResult.success ? pendingResult.data.pages : 0
        )
      }
      
      return { success: true, data: mergedData }
    } catch (err) {
      console.error('getMergedComments error:', err)
      return { success: false, message: '获取合并评论列表失败，请稍后重试' }
    } finally {
      // 不修改commentSubmitLock，只修改loading状态
      commentLoading.value = false
    }
  }

  return { 
    getCommentsByArticle, 
    createComment, 
    likeComment, 
    reportComment, 
    getAdminReports, 
    resolveReport, 
    getAllCommentsAdmin, 
    getPendingComments, 
    auditComment, 
    batchAuditComments,
    getMergedComments
  }
}
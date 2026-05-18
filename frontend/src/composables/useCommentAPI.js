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

      // 后端返回的是直接的评论数组，不是分页对象
      const commentsArray = Array.isArray(data.value) ? data.value : []
      
      const safeData = {
        items: commentsArray,
        total: commentsArray.length
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

  // 更新评论
  const updateComment = async (id, commentData) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '更新正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/:id', { id })
      const { data, error } = await useBaseFetch(url).put(commentData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '更新评论') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('updateComment error:', err)
      return { success: false, message: '更新评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 删除评论
  const deleteComment = async (id) => {
    if (commentSubmitLock.value) {
      return { success: false, message: '删除正在进行中，请稍后...' }
    }
    
    commentLoading.value = true
    commentSubmitLock.value = true
    
    try {
      const url = buildUrl('/comments/:id', { id })
      const { data, error } = await useBaseFetch(url).delete().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '删除评论') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('deleteComment error:', err)
      return { success: false, message: '删除评论时发生未知错误，请稍后重试' }
    } finally {
      commentLoading.value = false
      commentSubmitLock.value = false
    }
  }

  // 点赞/取消点赞评论
  const toggleCommentLike = async (commentId) => {
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

  return { 
    getCommentsByArticle, 
    createComment, 
    updateComment, 
    deleteComment,
    toggleCommentLike,
    // 新增的loading状态和提交锁
    commentLoading,
    commentSubmitLock
  }
}
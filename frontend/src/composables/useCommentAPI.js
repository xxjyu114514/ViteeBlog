import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useCommentAPI() {
  
  // 获取文章评论列表
  const getCommentsByArticle = async (articleId, params = {}) => {
    const url = buildUrl('/comment/article/:article_id', { article_id: articleId }, params)
    const { data, error } = await useBaseFetch(url).get().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取评论') }
    }

    const safeData = {
      items: Array.isArray(data.value?.items) ? data.value.items : [],
      total: data.value?.total || 0
    }

    return { success: true, data: safeData }
  }

  // 创建评论
  const createComment = async (commentData) => {
    const url = buildUrl('/comment/')
    const { data, error } = await useBaseFetch(url).post(commentData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '发表评论') }
    }
    return { success: true, data: data.value }
  }

  // 更新评论
  const updateComment = async (id, commentData) => {
    const url = buildUrl('/comment/:id', { id })
    const { data, error } = await useBaseFetch(url).put(commentData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '更新评论') }
    }
    return { success: true, data: data.value }
  }

  // 删除评论
  const deleteComment = async (id) => {
    const url = buildUrl('/comment/:id', { id })
    const { data, error } = await useBaseFetch(url).delete().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '删除评论') }
    }
    return { success: true, data: data.value }
  }

  return { getCommentsByArticle, createComment, updateComment, deleteComment }
}
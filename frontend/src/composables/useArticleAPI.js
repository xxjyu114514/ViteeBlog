import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useArticleAPI() {

  // 自动保存/创建文章
  const autoSaveArticle = async (articleData) => {
    const url = buildUrl('/article/autosave')
    const { data, error } = await useBaseFetch(url).post(articleData).json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '保存文章') }
    }
    
    return { success: true, data: data.value }
  }

  // 获取文章详情
  const getArticleDetail = async (articleId) => {
    const url = buildUrl('/article/:id', { id: articleId })
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取文章') }
    }
    
    return { success: true, data: data.value }
  }

  // 发布文章
  const publishArticle = async (articleId) => {
    const url = buildUrl('/article/:id/publish', { id: articleId })
    const { data, error } = await useBaseFetch(url).put({}).json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '发布文章') }
    }
    
    return { success: true }
  }

  // 获取公开文章列表（支持分页和分类筛选）
  const getPublicArticles = async (categoryId = null, page = 1, size = 10) => {
    const queryParams = {}
    if (categoryId) {
      queryParams.category_id = categoryId
    }
    queryParams.page = page
    queryParams.size = size
    
    const url = buildUrl('/article/public/list', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取文章列表') }
    }

    // 防御性编程：确保返回的结构安全
    const safeData = {
      items: Array.isArray(data.value?.items) ? data.value.items : [],
      total: data.value?.total || 0,
      page: data.value?.page || page,
      pages: data.value?.pages || 0
    }
    
    return { success: true, data: safeData }
  }

  // 获取用户自己的文章列表（支持分页）
  const getMyArticles = async (page = 1, size = 10) => {
    const queryParams = {
      page: page,
      size: size
    }
    
    const url = buildUrl('/article/my/list', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取我的文章') }
    }

    // 防御性编程：确保返回的结构安全
    const safeData = {
      items: Array.isArray(data.value?.items) ? data.value.items : [],
      total: data.value?.total || 0,
      page: data.value?.page || page,
      pages: data.value?.pages || 0
    }
    
    return { success: true, data: safeData }
  }

  // 软删除文章（移至回收站）
  const softDeleteArticle = async (articleId) => {
    const url = buildUrl('/article/:id', { id: articleId })
    const { data, error } = await useBaseFetch(url).delete().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '删除文章') }
    }
    
    return { success: true }
  }

  // 恢复文章
  const restoreArticle = async (articleId) => {
    const url = buildUrl('/article/:id/restore', { id: articleId })
    const { data, error } = await useBaseFetch(url).post({}).json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '恢复文章') }
    }
    
    return { success: true }
  }

  // 管理员审核文章
  const reviewArticle = async (articleId, passAudit, remark = '') => {
    // 如果是驳回但没有提供有效的remark，返回错误
    if (!passAudit && (!remark || !remark.trim())) {
      return { success: false, message: '驳回文章必须填写原因' }
    }

    const url = buildUrl('/article/admin/articles/:id/review', { id: articleId })
    const reviewData = {
      pass_audit: passAudit
    }
    // 只有在驳回时才添加remark字段，且确保是非空字符串
    if (!passAudit && remark && remark.trim()) {
      reviewData.remark = remark.trim()
    }
    
    const { data, error } = await useBaseFetch(url).post(reviewData).json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '审核文章') }
    }
    
    return { success: true }
  }

  // 获取全站文章列表（管理员专用）
  const getAdminAllArticles = async (page = 1, size = 20, showDeleted = false) => {
    const queryParams = {
      page: page,
      size: size,
      show_deleted: showDeleted
    }
    
    const url = buildUrl('/article/admin/all-articles', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取全站文章') }
    }

    // 防御性编程：确保返回的结构安全
    const safeData = {
      items: Array.isArray(data.value?.items) ? data.value.items : [],
      total: data.value?.total || 0,
      page: data.value?.page || page,
      pages: data.value?.pages || 0
    }
    
    return { success: true, data: safeData }
  }

  // 撤回发布（从待审核状态撤回到草稿）
  const withdrawArticle = async (articleId) => {
    const url = buildUrl('/article/:id/withdraw', { id: articleId })
    const { data, error } = await useBaseFetch(url).post({}).json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '撤回发布') }
    }
    
    return { success: true }
  }

  return {
    autoSaveArticle,
    getArticleDetail,
    publishArticle,
    getPublicArticles,
    getMyArticles,
    softDeleteArticle,
    restoreArticle,
    reviewArticle,
    getAdminAllArticles,
    withdrawArticle
  }
}
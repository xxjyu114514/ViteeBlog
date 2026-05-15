import { ref } from 'vue'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useArticleAPI() {
  // 文章操作的loading状态
  const articleLoading = ref(false)
  // 防重复提交锁
  const articleSubmitLock = ref(false)

  // 自动保存/创建文章
  const autoSaveArticle = async (articleData) => {
    // 检查是否正在提交中
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/autosave')
      const { data, error } = await useBaseFetch(url).post(articleData).json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '保存文章') }
      }
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('autoSaveArticle error:', err)
      return { success: false, message: '保存文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
  }

  // 获取文章详情
  const getArticleDetail = async (articleId) => {
    articleLoading.value = true
    
    try {
      const url = buildUrl('/article/:id', { id: articleId })
      const { data, error } = await useBaseFetch(url).get().json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取文章') }
      }
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('getArticleDetail error:', err)
      return { success: false, message: '获取文章详情时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
    }
  }

  // 发布文章
  const publishArticle = async (articleId) => {
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/:id/publish', { id: articleId })
      const { data, error } = await useBaseFetch(url).put({}).json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '发布文章') }
      }
      
      return { success: true }
    } catch (err) {
      console.error('publishArticle error:', err)
      return { success: false, message: '发布文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
  }

  // 获取公开文章列表（支持分页和分类筛选）
  const getPublicArticles = async (categoryId = null, page = 1, size = 10) => {
    articleLoading.value = true
    
    try {
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
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('getPublicArticles error:', err)
      return { success: false, message: '获取文章列表时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
    }
  }

  // 获取我的文章列表
  const getMyArticles = async (status = null, page = 1, size = 10) => {
    articleLoading.value = true
    
    try {
      const queryParams = { page, size }
      if (status !== null) {
        queryParams.status = status
      }
      
      const url = buildUrl('/article/my/list', {}, queryParams)
      const { data, error } = await useBaseFetch(url).get().json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取我的文章') }
      }
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('getMyArticles error:', err)
      return { success: false, message: '获取我的文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
    }
  }

  // 软删除文章
  const softDeleteArticle = async (articleId) => {
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/:id/soft-delete', { id: articleId })
      const { data, error } = await useBaseFetch(url).delete().json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '删除文章') }
      }
      
      return { success: true }
    } catch (err) {
      console.error('softDeleteArticle error:', err)
      return { success: false, message: '删除文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
  }

  // 恢复文章
  const restoreArticle = async (articleId) => {
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/:id/restore', { id: articleId })
      const { data, error } = await useBaseFetch(url).put({}).json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '恢复文章') }
      }
      
      return { success: true }
    } catch (err) {
      console.error('restoreArticle error:', err)
      return { success: false, message: '恢复文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
  }

  // 审核文章
  const reviewArticle = async (articleId, action) => {
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/:id/review', { id: articleId })
      const { data, error } = await useBaseFetch(url).put({ action }).json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '审核文章') }
      }
      
      return { success: true }
    } catch (err) {
      console.error('reviewArticle error:', err)
      return { success: false, message: '审核文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
  }

  // 获取管理员所有文章
  const getAdminAllArticles = async (status = null, page = 1, size = 10) => {
    articleLoading.value = true
    
    try {
      const queryParams = { page, size }
      if (status !== null) {
        queryParams.status = status
      }
      
      const url = buildUrl('/article/admin/all', {}, queryParams)
      const { data, error } = await useBaseFetch(url).get().json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取所有文章') }
      }
      
      return { success: true, data: data.value }
    } catch (err) {
      console.error('getAdminAllArticles error:', err)
      return { success: false, message: '获取所有文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
    }
  }

  // 撤回文章
  const withdrawArticle = async (articleId) => {
    if (articleSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    articleLoading.value = true
    articleSubmitLock.value = true
    
    try {
      const url = buildUrl('/article/:id/withdraw', { id: articleId })
      const { data, error } = await useBaseFetch(url).put({}).json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '撤回文章') }
      }
      
      return { success: true }
    } catch (err) {
      console.error('withdrawArticle error:', err)
      return { success: false, message: '撤回文章时发生未知错误，请稍后重试' }
    } finally {
      articleLoading.value = false
      articleSubmitLock.value = false
    }
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
    withdrawArticle,
    // 新增的loading状态和提交锁
    articleLoading,
    articleSubmitLock
  }
}
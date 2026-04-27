import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { getBaseUrl } from '@/config/apiConfig'
import { buildUrl } from '@/utils/apiUtils'

// 创建一个预配置的 fetch 实例
const useBaseFetch = createFetch({
  baseUrl: getBaseUrl(),
  options: {
    async beforeFetch({ options }) {
      const userStore = useUserStore()
      if (userStore.token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${userStore.token}`,
        }
      }
      return { options }
    },
    onFetchError(ctx) {
      // 全局处理：例如 401 自动登出
      if (ctx.response?.status === 401) {
        const userStore = useUserStore()
        const router = useRouter()
        userStore.logout()
        // 使用 Vue Router 跳转而不是 window.location
        router.push('/login')
      }
      return ctx
    },
  },
  fetchOptions: {
    mode: 'cors',
  },
})

// 统一的错误信息提取函数
const extractFriendlyErrorMessage = (error, context = '操作') => {
  // 开发者调试信息（保留详细错误）
  if (error) {
    console.error(`🐛 ${context}错误详情:`, {
      status: error.status,
      message: error.message,
      data: error.data,
      url: error.url
    })
  }
  
  // 用户友好提示
  if (!error) {
    return `${context}失败，请稍后重试`
  }
  
  // 优先使用后端返回的具体错误详情
  if (error.data?.detail) {
    return error.data.detail
  }
  
  // 根据HTTP状态码提供友好提示
  switch (error.status) {
    case 400:
      return '输入信息有误，请检查后重试'
    case 401:
      return '身份验证失败，请重新登录'
    case 403:
      return '权限不足，仅博主可操作'
    case 404:
      return '文章不存在或已被删除'
    case 429:
      return '操作太频繁，请稍后再试'
    case 500:
      return '系统繁忙，请稍后重试'
    case 502:
    case 503:
    case 504:
      return '服务暂时不可用，请稍后重试'
    default:
      return `${context}失败，请稍后重试`
  }
}

export function useArticleAPI() {
  const userStore = useUserStore()

  // 自动保存/创建文章
  const autoSaveArticle = async (articleData) => {
    const { data, error } = await useBaseFetch('/article/autosave').post(articleData).json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '保存文章')
    return { success: false, message: errorMessage }
  }

  // 获取文章详情
  const getArticleDetail = async (articleId) => {
    const url = buildUrl('/article/:id', { id: articleId })
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取文章')
    return { success: false, message: errorMessage }
  }

  // 发布文章
  const publishArticle = async (articleId) => {
    try {
      const url = buildUrl('/article/:id/publish', { id: articleId })
      const { data, error } = await useBaseFetch(url).put({}).json()
      
      if (!error.value) {
        return { success: true }
      }
      
      const errorMessage = extractFriendlyErrorMessage(error.value, '发布文章')
      console.error('🐛 发布文章详细错误:', error.value)
      return { success: false, message: errorMessage }
    } catch (err) {
      console.error('🔥 发布文章异常:', err)
      return { success: false, message: '发布失败：网络错误或服务器异常' }
    }
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
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取文章列表')
    return { success: false, message: errorMessage }
  }

  // 获取用户自己的文章列表（支持分页）
  const getMyArticles = async (page = 1, size = 10) => {
    const queryParams = {
      page: page,
      size: size
    }
    
    const url = buildUrl('/article/my/list', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取我的文章')
    return { success: false, message: errorMessage }
  }

  // 软删除文章（移至回收站）
  const softDeleteArticle = async (articleId) => {
    const url = buildUrl('/article/:id', { id: articleId })
    const { data, error } = await useBaseFetch(url).delete().json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '删除文章')
    return { success: false, message: errorMessage }
  }

  // 恢复文章
  const restoreArticle = async (articleId) => {
    const url = buildUrl('/article/:id/restore', { id: articleId })
    const { data, error } = await useBaseFetch(url).post({}).json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '恢复文章')
    return { success: false, message: errorMessage }
  }

  // 管理员审核文章
  const reviewArticle = async (articleId, passAudit, remark = '') => {
    const url = buildUrl('/article/admin/articles/:id/review', { id: articleId })
    const reviewData = {
      pass_audit: passAudit
    }
    // 只有在驳回时才添加remark字段，且确保是非空字符串
    if (!passAudit && remark && remark.trim()) {
      reviewData.remark = remark.trim()
    }
    // 如果是驳回但没有提供有效的remark，返回错误
    if (!passAudit && (!remark || !remark.trim())) {
      return { success: false, message: '驳回文章必须填写原因' }
    }
    
    const { data, error } = await useBaseFetch(url).post(reviewData).json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '审核文章')
    return { success: false, message: errorMessage }
  }

  return {
    autoSaveArticle,
    getArticleDetail,
    publishArticle,
    getPublicArticles,
    getMyArticles,
    softDeleteArticle,
    restoreArticle,
    reviewArticle
  }
}
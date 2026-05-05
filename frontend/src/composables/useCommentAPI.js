import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
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
        userStore.logout()
        // 在composable中不能使用useRouter，改用window.location
        window.location.href = '/login'
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
  // 用户友好提示
  if (!error) {
    return `${context}失败，请稍后重试`
  }
  
  // 优先使用后端返回的具体错误详情
  if (error.data?.detail) {
    return error.data.detail
  }
  
  // 特别处理422错误，显示具体的验证错误
  if (error.status === 422 && error.data) {
    // FastAPI的422错误通常包含detail字段数组
    if (Array.isArray(error.data.detail)) {
      const messages = error.data.detail.map(item => {
        if (typeof item === 'string') {
          return item;
        }
        // 处理Pydantic验证错误格式
        if (item.loc && item.msg) {
          const field = item.loc.slice(1).join('.');
          return `${field}: ${item.msg}`;
        }
        return JSON.stringify(item);
      });
      return `${context}失败：${messages.join('；')}`;
    }
    // 如果是其他格式的422错误
    return `${context}失败：${JSON.stringify(error.data)}`;
  }
  
  // 根据HTTP状态码提供友好提示
  switch (error.status) {
    case 400:
      return '输入信息有误，请检查后重试'
    case 401:
      return '身份验证失败，请重新登录'
    case 403:
      return '权限不足'
    case 404:
      return '请求的资源不存在'
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

export function useCommentAPI() {
  const userStore = useUserStore()

  // 发表评论
  const postComment = async (articleId, content, parentId = null) => {
    const url = buildUrl('/comments/articles/:id/comments', { id: articleId })
    const commentData = {
      content: content
    }
    if (parentId !== null) {
      commentData.parent_id = parentId
    }
    
    const { data, error } = await useBaseFetch(url).post(commentData).json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '发表评论')
    return { success: false, message: errorMessage }
  }

  // 获取文章评论列表
  const getComments = async (articleId) => {
    const url = buildUrl('/comments/articles/:id/comments', { id: articleId })
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (!error.value) {
      // 安全检查：确保data.value存在且为数组
      const commentsData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: commentsData }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取评论')
    return { success: false, message: errorMessage }
  }

  // 删除评论
  const deleteComment = async (commentId) => {
    const url = buildUrl('/comments/:id', { id: commentId })
    const { data, error } = await useBaseFetch(url).delete().json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '删除评论')
    return { success: false, message: errorMessage }
  }

  // 举报评论
  const reportComment = async (commentId, reason) => {
    const url = buildUrl('/comments/:id/report', { id: commentId })
    const reportData = {
      reason: reason
    }
    
    const { data, error } = await useBaseFetch(url).post(reportData).json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '举报评论')
    return { success: false, message: errorMessage }
  }

  // 获取举报列表（管理员专用）
  const getReports = async () => {
    const { data, error } = await useBaseFetch('/comments/admin/reports').get().json()
    
    if (!error.value) {
      // 安全检查：确保data.value存在且为数组
      const reportsData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: reportsData }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取举报列表')
    return { success: false, message: errorMessage }
  }

  // 处理举报（标记为已解决）
  const resolveReport = async (reportId) => {
    const url = buildUrl('/comments/admin/reports/:id/resolve', { id: reportId })
    const { data, error } = await useBaseFetch(url).put({}).json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '处理举报')
    return { success: false, message: errorMessage }
  }

  // 管理员全站评论巡查（分页）
  const getAdminAllComments = async (page = 1, size = 20) => {
    const queryParams = {
      page: page,
      size: size
    }
    
    const url = buildUrl('/comments/admin/comments/all', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (!error.value) {
      // 安全检查：确保data.value存在
      const responseData = data.value || { items: [], total: 0, page: page, pages: 0 }
      return { success: true, data: responseData }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取全站评论')
    return { success: false, message: errorMessage }
  }

  // 点赞/取消点赞评论
  const toggleCommentLike = async (commentId) => {
    const url = buildUrl('/comments/:id/like', { id: commentId })
    const { data, error } = await useBaseFetch(url).post({}).json()
    
    if (!error.value) {
      return { success: true }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '点赞操作')
    return { success: false, message: errorMessage }
  }

  return {
    postComment,
    getComments,
    deleteComment,
    reportComment,
    getReports,
    resolveReport,
    getAdminAllComments,
    toggleCommentLike
  }
}
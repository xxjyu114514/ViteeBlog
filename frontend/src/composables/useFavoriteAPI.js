import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useFavoriteAPI() {
  
  // 收藏/取消收藏文章
  const toggleFavorite = async (articleId) => {
    const url = buildUrl('/favorites/:article_id/favorite', { article_id: articleId })
    const { data, error } = await useBaseFetch(url).post({}).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '收藏操作') }
    }
    
    return { 
      success: true, 
      favorited: data.value.favorited,
      message: data.value.message 
    }
  }

  // 获取我的收藏列表
  const getMyFavorites = async (page = 1, size = 10) => {
    const queryParams = {
      page: page,
      size: size
    }
    
    const url = buildUrl('/favorites/my', {}, queryParams)
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取收藏列表') }
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

  // 检查收藏状态
  const checkFavoriteStatus = async (articleId) => {
    const url = buildUrl('/favorites/check/:article_id', { article_id: articleId })
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '检查收藏状态') }
    }
    
    return { 
      success: true, 
      favorited: data.value.favorited 
    }
  }

  return { 
    toggleFavorite, 
    getMyFavorites, 
    checkFavoriteStatus 
  }
}
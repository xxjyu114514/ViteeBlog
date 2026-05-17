import { ref } from 'vue'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useFavoriteAPI() {
  // 收藏操作的loading状态
  const favoriteLoading = ref(false)
  // 防重复提交锁
  const favoriteSubmitLock = ref(false)
  
  // 收藏/取消收藏文章
  const toggleFavorite = async (articleId) => {
    if (favoriteSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    favoriteLoading.value = true
    favoriteSubmitLock.value = true
    
    try {
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
    } catch (err) {
      console.error('toggleFavorite error:', err)
      return { success: false, message: '收藏操作时发生未知错误，请稍后重试' }
    } finally {
      favoriteLoading.value = false
      favoriteSubmitLock.value = false
    }
  }

  // 获取我的收藏列表
  const getMyFavorites = async (page = 1, size = 10) => {
    favoriteLoading.value = true
    
    try {
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
    } catch (err) {
      console.error('getMyFavorites error:', err)
      return { success: false, message: '获取收藏列表时发生未知错误，请稍后重试' }
    } finally {
      favoriteLoading.value = false
    }
  }

  // 检查收藏状态
  const checkFavoriteStatus = async (articleId) => {
    favoriteLoading.value = true
    
    try {
      const url = buildUrl('/favorites/check/:article_id', { article_id: articleId })
      const { data, error } = await useBaseFetch(url).get().json()
      
      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '检查收藏状态') }
      }
      
      return { 
        success: true, 
        favorited: data.value.favorited 
      }
    } catch (err) {
      console.error('checkFavoriteStatus error:', err)
      return { success: false, message: '检查收藏状态时发生未知错误，请稍后重试' }
    } finally {
      favoriteLoading.value = false
    }
  }

  return { 
    toggleFavorite, 
    getMyFavorites, 
    checkFavoriteStatus,
    // 新增的loading状态和提交锁
    favoriteLoading,
    favoriteSubmitLock
  }
}
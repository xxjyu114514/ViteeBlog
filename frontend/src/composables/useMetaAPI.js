import { ref } from 'vue'
import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useMetaAPI() {
  // 元数据操作的loading状态
  const metaLoading = ref(false)
  // 防重复提交锁
  const metaSubmitLock = ref(false)
  
  // 获取分类列表
  const getCategories = async () => {
    metaLoading.value = true
    
    try {
      const url = buildUrl('/meta/categories')
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取分类') }
      }

      const safeData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: safeData }
    } catch (err) {
      console.error('getCategories error:', err)
      return { success: false, message: '获取分类时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
    }
  }

  // 创建分类
  const createCategory = async (categoryName) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/categories')
      // 后端期望 {name: "分类名"} 格式
      const requestData = { name: categoryName }
      const { data, error } = await useBaseFetch(url).post(requestData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '创建分类') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('createCategory error:', err)
      return { success: false, message: '创建分类时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  // 更新分类
  const updateCategory = async (id, categoryName) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/categories/:id', { id })
      // 后端期望 {name: "分类名"} 格式
      const requestData = { name: categoryName }
      const { data, error } = await useBaseFetch(url).put(requestData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '更新分类') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('updateCategory error:', err)
      return { success: false, message: '更新分类时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  // 删除分类
  const deleteCategory = async (id) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/categories/:id', { id })
      const { data, error } = await useBaseFetch(url).delete().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '删除分类') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('deleteCategory error:', err)
      return { success: false, message: '删除分类时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  // 获取标签列表
  const getTags = async () => {
    metaLoading.value = true
    
    try {
      const url = buildUrl('/meta/tags')
      const { data, error } = await useBaseFetch(url).get().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '获取标签') }
      }

      const safeData = Array.isArray(data.value) ? data.value : []
      return { success: true, data: safeData }
    } catch (err) {
      console.error('getTags error:', err)
      return { success: false, message: '获取标签时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
    }
  }

  // 创建标签
  const createTag = async (tagName) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/tags')
      // 后端期望 {name: "标签名"} 格式
      const requestData = { name: tagName }
      const { data, error } = await useBaseFetch(url).post(requestData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '创建标签') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('createTag error:', err)
      return { success: false, message: '创建标签时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  // 更新标签
  const updateTag = async (id, tagName) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/tags/:id', { id })
      // 后端期望 {name: "标签名"} 格式
      const requestData = { name: tagName }
      const { data, error } = await useBaseFetch(url).put(requestData).json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '更新标签') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('updateTag error:', err)
      return { success: false, message: '更新标签时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  // 删除标签
  const deleteTag = async (id) => {
    if (metaSubmitLock.value) {
      return { success: false, message: '操作正在进行中，请稍后...' }
    }
    
    metaLoading.value = true
    metaSubmitLock.value = true
    
    try {
      const url = buildUrl('/meta/tags/:id', { id })
      const { data, error } = await useBaseFetch(url).delete().json()

      if (error.value) {
        return { success: false, message: handleFriendlyError(error.value, '删除标签') }
      }
      return { success: true, data: data.value }
    } catch (err) {
      console.error('deleteTag error:', err)
      return { success: false, message: '删除标签时发生未知错误，请稍后重试' }
    } finally {
      metaLoading.value = false
      metaSubmitLock.value = false
    }
  }

  return { 
    getCategories, createCategory, updateCategory, deleteCategory,
    getTags, createTag, updateTag, deleteTag,
    // 新增的loading状态和提交锁
    metaLoading,
    metaSubmitLock
  }
}
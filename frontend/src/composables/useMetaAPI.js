import { useBaseFetch, handleFriendlyError } from '@/api/client'
import { buildUrl } from '@/utils/apiUtils'

export function useMetaAPI() {
  
  // 获取分类列表
  const getCategories = async () => {
    const url = buildUrl('/meta/categories')
    const { data, error } = await useBaseFetch(url).get().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取分类') }
    }

    const safeData = Array.isArray(data.value) ? data.value : []
    return { success: true, data: safeData }
  }

  // 创建分类
  const createCategory = async (categoryData) => {
    const url = buildUrl('/meta/categories')
    const { data, error } = await useBaseFetch(url).post(categoryData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '创建分类') }
    }
    return { success: true, data: data.value }
  }

  // 更新分类
  const updateCategory = async (id, categoryData) => {
    const url = buildUrl('/meta/categories/:id', { id })
    const { data, error } = await useBaseFetch(url).put(categoryData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '更新分类') }
    }
    return { success: true, data: data.value }
  }

  // 删除分类
  const deleteCategory = async (id) => {
    const url = buildUrl('/meta/categories/:id', { id })
    const { data, error } = await useBaseFetch(url).delete().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '删除分类') }
    }
    return { success: true, data: data.value }
  }

  // 获取标签列表
  const getTags = async () => {
    const url = buildUrl('/meta/tags')
    const { data, error } = await useBaseFetch(url).get().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '获取标签') }
    }

    const safeData = Array.isArray(data.value) ? data.value : []
    return { success: true, data: safeData }
  }

  // 创建标签
  const createTag = async (tagData) => {
    const url = buildUrl('/meta/tags')
    const { data, error } = await useBaseFetch(url).post(tagData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '创建标签') }
    }
    return { success: true, data: data.value }
  }

  // 更新标签
  const updateTag = async (id, tagData) => {
    const url = buildUrl('/meta/tags/:id', { id })
    const { data, error } = await useBaseFetch(url).put(tagData).json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '更新标签') }
    }
    return { success: true, data: data.value }
  }

  // 删除标签
  const deleteTag = async (id) => {
    const url = buildUrl('/meta/tags/:id', { id })
    const { data, error } = await useBaseFetch(url).delete().json()

    if (error.value) {
      return { success: false, message: handleFriendlyError(error.value, '删除标签') }
    }
    return { success: true, data: data.value }
  }

  return { 
    getCategories, createCategory, updateCategory, deleteCategory,
    getTags, createTag, updateTag, deleteTag 
  }
}
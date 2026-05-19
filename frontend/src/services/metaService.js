/**
 * 元数据服务 — /api/v1/meta/*（分类 & 标签）
 */
import { get, post, put, del } from '@/api/client'

// ---- 分类 ----

/** GET /meta/categories */
export const getCategories = () =>
  get('/meta/categories')

/** POST /meta/categories */
export const createCategory = (name) =>
  post('/meta/categories', { name })

/** PUT /meta/categories/{id} */
export const updateCategory = (id, name) =>
  put(`/meta/categories/${id}`, { name })

/** DELETE /meta/categories/{id} */
export const deleteCategory = (id) =>
  del(`/meta/categories/${id}`)

// ---- 标签 ----

/** GET /meta/tags */
export const getTags = () =>
  get('/meta/tags')

/** POST /meta/tags */
export const createTag = (name) =>
  post('/meta/tags', { name })

/** PUT /meta/tags/{id} */
export const updateTag = (id, name) =>
  put(`/meta/tags/${id}`, { name })

/** DELETE /meta/tags/{id} */
export const deleteTag = (id) =>
  del(`/meta/tags/${id}`)

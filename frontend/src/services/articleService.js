/**
 * 文章服务 — /api/v1/article/*
 * 所有函数返回 ApiResponse 格式
 */
import { get, post, put, del, uploadFile } from '@/api/client'

/** GET /article/public/list */
export const getPublicArticles = (params = {}) =>
  get('/article/public/list', params)

/** GET /article/{id} */
export const getArticleDetail = (id) =>
  get(`/article/${id}`)

/** GET /article/my/list */
export const getMyArticles = (params = {}) =>
  get('/article/my/list', params)

/** GET /article/admin/all-articles */
export const getAdminAllArticles = (params = {}) =>
  get('/article/admin/all-articles', params)

/** GET /article/admin/pending */
export const getPendingArticles = (params = {}) =>
  get('/article/admin/pending', params)

/** POST /article/autosave */
export const autoSaveArticle = (articleData) =>
  post('/article/autosave', articleData)

/** PUT /article/{id}/publish */
export const publishArticle = (id) =>
  put(`/article/${id}/publish`, {})

/** POST /article/{id}/withdraw */
export const withdrawArticle = (id) =>
  post(`/article/${id}/withdraw`)

/** DELETE /article/{id} （软删除） */
export const softDeleteArticle = (id) =>
  del(`/article/${id}`)

/** DELETE /article/{id}/hard */
export const hardDeleteArticle = (id) =>
  del(`/article/${id}/hard`)

/** POST /article/{id}/restore */
export const restoreArticle = (id) =>
  post(`/article/${id}/restore`)

/** POST /article/{id}/like */
export const toggleArticleLike = (id) =>
  post(`/article/${id}/like`, {})

/** GET /article/{id}/like/count */
export const getArticleLikeCount = (id) =>
  get(`/article/${id}/like/count`)

/** POST /article/upload-image */
export const uploadArticleImage = (file) =>
  uploadFile('/article/upload-image', file, 'file')

/** DELETE /article/upload-image */
export const deleteArticleImage = (filename) =>
  del('/article/upload-image', { params: { filename } })

/** POST /article/admin/articles/{id}/review */
export const reviewArticle = (id, action) =>
  post(`/article/admin/articles/${id}/review`, action)

/** PUT /article/admin/articles/{id}/pin */
export const togglePinArticle = (id) =>
  put(`/article/admin/articles/${id}/pin`, {})

/** GET /article/public/archive */
export const getArticleArchive = () =>
  get('/article/public/archive')

/** GET /article/my/pending-count */
export const getMyPendingCount = () =>
  get('/article/my/pending-count')

/** GET /article/public/search */
export const searchArticles = (params = {}) =>
  get('/article/public/search', params)

/** POST /article/admin/import/single */
export const importSingleArticle = (file) =>
  uploadFile('/article/admin/import/single', file, 'file')

/** POST /article/admin/import/batch */
export const importBatchArticles = (files) =>
  uploadFile('/article/admin/import/batch', files, 'files')

/** POST /article/admin/upload-images/batch */
export const batchUploadImages = (file) =>
  uploadFile('/article/admin/upload-images/batch', file, 'file')

/** GET /users/{userId}/articles */
export const getUserArticles = (userId, params = {}) =>
  get(`/users/${userId}/articles`, params)

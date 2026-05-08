/**
 * 构建完整的API URL，支持路径参数替换和查询参数拼接
 * @param {string} path - API路径模板，如 '/article/:id'
 * @param {Object} pathParams - 路径参数，如 { id: 123 }
 * @param {Object} queryParams - 查询参数，如 { page: 1, size: 10 }
 * @param {string} apiType - API类型，如 'ARTICLE', 'META'，默认为 'ARTICLE'
 * @returns {string} 完整的URL
 */
import { getBaseUrl } from '@/config/apiConfig'

/**
 * 动态构建 URL：处理 RESTful 路径参数和 Query 字符串
 * @example buildUrl('/article/:id', { id: 123 }, { page: 1 }) => '/article/123?page=1'
 */
export const buildUrl = (path, pathParams = {}, queryParams = {}) => {
  let finalPath = path

  // 1. 替换路径参数 (如 :id)
  for (const [key, value] of Object.entries(pathParams)) {
    finalPath = finalPath.replace(`:${key}`, encodeURIComponent(value))
  }

  // 2. 拼接 Query 参数
  if (Object.keys(queryParams).length > 0) {
    // 过滤掉 undefined 或 null 的参数
    const cleanQuery = Object.fromEntries(
      Object.entries(queryParams).filter(([_, v]) => v != null && v !== '')
    )
    const queryString = new URLSearchParams(cleanQuery).toString()
    if (queryString) {
      finalPath += `?${queryString}`
    }
  }

  return finalPath
}

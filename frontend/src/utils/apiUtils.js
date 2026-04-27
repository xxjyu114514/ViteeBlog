/**
 * 构建完整的API URL，支持路径参数替换和查询参数拼接
 * @param {string} path - API路径模板，如 '/article/:id'
 * @param {Object} pathParams - 路径参数，如 { id: 123 }
 * @param {Object} queryParams - 查询参数，如 { page: 1, size: 10 }
 * @param {string} apiType - API类型，如 'ARTICLE', 'META'，默认为 'ARTICLE'
 * @returns {string} 完整的URL
 */
import { getBaseUrl } from '@/config/apiConfig'

export function buildUrl(path, pathParams = {}, queryParams = {}, apiType = 'ARTICLE') {
  // 获取基础URL
  const baseUrl = getBaseUrl()
  
  // 根据API类型确定前缀
  let fullUrl = baseUrl + path
  
  // 替换路径参数占位符
  Object.keys(pathParams).forEach(key => {
    const placeholder = `:${key}`
    if (fullUrl.includes(placeholder)) {
      fullUrl = fullUrl.replace(placeholder, encodeURIComponent(pathParams[key]))
    }
  })
  
  // 拼接查询参数
  if (Object.keys(queryParams).length > 0) {
    const params = new URLSearchParams()
    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] !== null && queryParams[key] !== undefined) {
        params.append(key, queryParams[key])
      }
    })
    if (params.toString()) {
      fullUrl += `?${params.toString()}`
    }
  }
  
  return fullUrl
}
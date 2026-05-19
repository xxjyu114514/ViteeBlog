/**
 * API 客户端 — 网络请求基础设施
 *
 * 职责：
 * 1. 统一的 fetch 封装（get/post/put/del）
 * 2. Token 自动注入
 * 3. 401 自动登出
 * 4. 统一的错误处理
 * 5. snake_case ↔ camelCase 转换
 */

import { useUserStore } from '@/stores/user'

// ============================================================
// 配置
// ============================================================

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const TIMEOUT_MS = 10000

// ============================================================
// snake_case ↔ camelCase 转换工具
// ============================================================

const snakeToCamel = (str) =>
  str.replace(/_([a-z])/g, (_, c) => c.toUpperCase())

const camelToSnake = (str) =>
  str.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`)

const isPlainObject = (val) =>
  val !== null && typeof val === 'object' && !Array.isArray(val)

const convertKeys = (obj, converter) => {
  if (Array.isArray(obj)) return obj.map((item) => convertKeys(item, converter))
  if (isPlainObject(obj)) {
    const result = {}
    for (const [key, value] of Object.entries(obj)) {
      result[converter(key)] = convertKeys(value, converter)
    }
    return result
  }
  return obj
}

/** 将响应数据从 snake_case 转为 camelCase */
export const toCamelCase = (data) => convertKeys(data, snakeToCamel)

/** 将请求数据从 camelCase 转为 snake_case */
export const toSnakeCase = (data) => convertKeys(data, camelToSnake)

// ============================================================
// 统一错误类
// ============================================================

export class ApiError extends Error {
  constructor(status, detail, rawResponse) {
    super(detail || '未知错误')
    this.name = 'ApiError'
    this.status = status
    this.rawResponse = rawResponse
  }

  get friendlyMessage() {
    if (!this.status) return '网络连接失败，请检查网络后重试'
    const map = {
      400: '请求参数有误，请检查后重试',
      401: '登录已过期，请重新登录',
      403: '您没有权限执行此操作',
      404: '请求的资源不存在',
      408: '请求超时，请稍后再试',
      409: '数据已被他人修改，请刷新后重试',
      422: '数据格式校验失败',
      429: '操作过于频繁，请稍后再试',
      500: '服务器繁忙，请稍后重试',
      502: '网关错误，服务暂时不可用',
    }
    return map[this.status] || `操作失败 (${this.status})`
  }
}

// ============================================================
// 通用返回包装
// ============================================================

/**
 * @template T
 * @typedef {Object} ApiResponse
 * @property {boolean} success
 * @property {T|null} data
 * @property {string|null} message
 * @property {number|null} status
 */

/**
 * 构建统一返回
 * @template T
 * @param {{ data: T|null, message?: string|null, status?: number|null, success?: boolean }} opts
 * @returns {ApiResponse<T>}
 */
const createResponse = ({ data = null, message = null, status = null, success = true } = {}) => ({
  success,
  data,
  message,
  status,
})

// ============================================================
// 核心请求函数
// ============================================================

/**
 * 发起 API 请求
 * @param {string} path - 路径（不含 baseURL），如 /auth/login
 * @param {object} options
 * @param {string} [options.method='GET']
 * @param {object} [options.body] - 请求体，会自动转 snake_case
 * @param {object} [options.params] - URL 查询参数，会自动转 snake_case
 * @param {boolean} [options.skipAuth=false] - 是否跳过 token 注入
 * @param {boolean} [options.silentError=false] - 是否不触发 401 自动登出
 * @param {AbortSignal} [options.signal]
 * @returns {Promise<ApiResponse>}
 */
export async function request(path, options = {}) {
  const {
    method = 'GET',
    body,
    params,
    skipAuth = false,
    silentError = false,
    signal,
  } = options

  // 构造完整 URL
  let url = `${BASE_URL}${path}`

  // 拼接查询参数（转 snake_case）
  if (params && Object.keys(params).length > 0) {
    const clean = {}
    for (const [k, v] of Object.entries(params)) {
      if (v !== null && v !== undefined && v !== '') {
        clean[camelToSnake(k)] = v
      }
    }
    const qs = new URLSearchParams(clean).toString()
    if (qs) url += `?${qs}`
  }

  // 构造 headers
  const headers = { 'Content-Type': 'application/json' }
  if (!skipAuth) {
    const userStore = useUserStore()
    if (userStore.token) {
      headers['Authorization'] = `Bearer ${userStore.token}`
    }
  }

  // 构造 fetch 选项
  const fetchOptions = {
    method,
    headers,
    signal,
  }
  if (body) {
    fetchOptions.body = JSON.stringify(toSnakeCase(body))
  }

  // 超时控制
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS)
  fetchOptions.signal = signal || controller.signal

  try {
    const response = await fetch(url, fetchOptions)
    clearTimeout(timeoutId)

    // 空响应（204 No Content）
    if (response.status === 204) {
      return createResponse({ status: 204 })
    }

    // 解析 JSON
    let json
    try {
      json = await response.json()
    } catch {
      json = null
    }

    if (!response.ok) {
      // 401 统一处理 —— 排除登录/注册请求
      if (response.status === 401 && !silentError && !path.includes('/auth/login') && !path.includes('/auth/register')) {
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/login'
        return createResponse({ success: false, message: '登录已过期', status: 401 })
      }

      const detail = json?.detail || null
      return createResponse({
        success: false,
        data: json,
        message: detail,
        status: response.status,
      })
    }

    // 成功：数据转 camelCase
    return createResponse({
      data: toCamelCase(json),
      status: response.status,
    })
  } catch (err) {
    clearTimeout(timeoutId)
    if (err.name === 'AbortError') {
      return createResponse({ success: false, message: '请求超时，请稍后重试', status: 408 })
    }
    return createResponse({ success: false, message: '网络连接失败，请检查网络后重试', status: 0 })
  }
}

// ============================================================
// 快捷方法
// ============================================================

/** GET 请求 */
export const get = (path, params, options) =>
  request(path, { ...options, method: 'GET', params })

/** POST 请求 */
export const post = (path, body, options) =>
  request(path, { ...options, method: 'POST', body })

/** PUT 请求 */
export const put = (path, body, options) =>
  request(path, { ...options, method: 'PUT', body })

/** DELETE 请求 */
export const del = (path, options) =>
  request(path, { ...options, method: 'DELETE' })

/** 文件上传（不转 JSON，不转 snake_case） */
export const uploadFile = async (path, file, fieldName = 'file', extraFields = {}) => {
  const userStore = useUserStore()
  const formData = new FormData()
  formData.append(fieldName, file)
  for (const [k, v] of Object.entries(extraFields)) {
    formData.append(k, v)
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS * 3) // 上传给 30 秒

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: userStore.token ? { Authorization: `Bearer ${userStore.token}` } : {},
      body: formData,
      signal: controller.signal,
    })
    clearTimeout(timeoutId)

    const json = await response.json()
    if (!response.ok) {
      return createResponse({ success: false, message: json?.detail || '上传失败', status: response.status })
    }
    return createResponse({ data: toCamelCase(json), status: response.status })
  } catch (err) {
    clearTimeout(timeoutId)
    if (err.name === 'AbortError') {
      return createResponse({ success: false, message: '上传超时', status: 408 })
    }
    return createResponse({ success: false, message: '网络连接失败', status: 0 })
  }
}

/** 获取后端文件内容（如 content_path 指向的 Markdown 文件） */
export const fetchFileContent = async (contentPath) => {
  if (!contentPath) return createResponse({ success: false, message: '路径为空' })
  try {
    const backendBase = BASE_URL.replace('/api/v1', '')
    let normalized = contentPath.replace(/\\/g, '/')
    if (!normalized.startsWith('/')) normalized = '/' + normalized
    const url = `${backendBase}${normalized}`

    const response = await fetch(url)
    if (response.ok) {
      const text = await response.text()
      return createResponse({ data: text })
    }
    // 尝试回退路径
    const fallbackUrl = `${backendBase}/${contentPath.replace(/^\/+/, '').replace(/\\/g, '/')}`
    const fallbackResponse = await fetch(fallbackUrl)
    if (fallbackResponse.ok) {
      const text = await fallbackResponse.text()
      return createResponse({ data: text })
    }
    return createResponse({ success: false, message: '文件不存在' })
  } catch (err) {
    return createResponse({ success: false, message: '加载文件失败' })
  }
}

export default {
  request,
  get,
  post,
  put,
  del,
  uploadFile,
  fetchFileContent,
  toCamelCase,
  toSnakeCase,
  ApiError,
  BASE_URL,
}

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
// 请求缓存（仅对 GET 生效）
// ============================================================
const cacheStore = new Map()
const CACHE_TTL = 30_000 // 默认 30 秒

const getCacheKey = (path, params) => {
  if (!params) return path
  return `${path}?${JSON.stringify(params)}`
}

const getCached = (key) => {
  const entry = cacheStore.get(key)
  if (!entry) return null
  if (Date.now() > entry.expiresAt) {
    cacheStore.delete(key)
    return null
  }
  return entry.data
}

const setCache = (key, data, ttl = CACHE_TTL) => {
  cacheStore.set(key, { data, expiresAt: Date.now() + ttl })
}

// ============================================================
// 重试配置
// ============================================================
const MAX_RETRIES = 2
/** 需要重试的 HTTP 状态码 */
const isRetryableStatus = (status) =>
  status === 0 || status === 408 || status === 429 || status === 500 || status === 502 || status === 503

/** 延迟辅助 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

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
    cacheTTL,        // 仅对 GET 生效，传 null 或 0 跳过缓存
  } = options

  const isGet = method === 'GET'

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

  // ---- 缓存查找（仅 GET，必须显式传入 cacheTTL > 0 才生效） ----
  const cacheKey = isGet ? getCacheKey(path, params) : null
  if (isGet && cacheTTL && cacheTTL > 0) {
    const cached = getCached(cacheKey)
    if (cached) return cached
  }

  // ---- 真正发起请求（含重试） ----
  const doFetch = async (attempt) => {
    // 构造 headers
    const headers = { 'Content-Type': 'application/json' }
    if (!skipAuth) {
      const userStore = useUserStore()
      if (userStore.token) {
        headers['Authorization'] = `Bearer ${userStore.token}`
      }
    }

    // 超时控制器（始终创建，和用户 signal 共存）
    const timeoutController = new AbortController()
    const timeoutId = setTimeout(() => timeoutController.abort(), TIMEOUT_MS)

    // 桥接：用户 signal 触发时也取消 timeoutController
    if (signal) {
      if (signal.aborted) {
        clearTimeout(timeoutId)
        return createResponse({ success: false, message: '请求已取消', status: 0 })
      }
      signal.addEventListener('abort', () => timeoutController.abort(), { once: true })
    }

    // 合并信号：使用 timeoutController 的 signal
    const fetchOptions = { method, headers, signal: timeoutController.signal }
    if (body) {
      fetchOptions.body = JSON.stringify(toSnakeCase(body))
    }

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
          import('@/router').then(({ default: router }) => router.push('/login'))
          return createResponse({ success: false, message: '登录已过期', status: 401 })
        }

        // 可重试的错误，且未用完重试次数
        if (attempt < MAX_RETRIES && isRetryableStatus(response.status)) {
          const delay = Math.min(1000 * Math.pow(2, attempt), 4000) // 1s → 2s → 4s
          await sleep(delay)
          return doFetch(attempt + 1)
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
      const result = createResponse({
        data: toCamelCase(json),
        status: response.status,
      })

      // 缓存成功响应（仅 GET，且必须显式传入 cacheTTL > 0）
      if (isGet && cacheTTL && cacheTTL > 0) {
        setCache(cacheKey, result, cacheTTL ?? CACHE_TTL)
      }

      return result
    } catch (err) {
      clearTimeout(timeoutId)
      if (err.name === 'AbortError') {
        // 区分用户主动取消 vs 超时
        if (signal?.aborted) {
          return createResponse({ success: false, message: '请求已取消', status: 0 })
        }
        return createResponse({ success: false, message: '请求超时，请稍后重试', status: 408 })
      }

      // 网络错误可重试
      if (attempt < MAX_RETRIES) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 4000)
        await sleep(delay)
        return doFetch(attempt + 1)
      }

      return createResponse({ success: false, message: '网络连接失败，请检查网络后重试', status: 0 })
    }
  }

  return doFetch(0)
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

export default {
  request,
  get,
  post,
  put,
  del,
  uploadFile,
  toCamelCase,
  toSnakeCase,
  ApiError,
  BASE_URL,
}

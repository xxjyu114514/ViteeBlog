/**
 * API 地址统一配置
 *
 * 所有文件统一从此处引入 API_BASE_URL / BACKEND_BASE_URL，
 * 不再各自书写 import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
 */

/** API 基础路径（如 http://localhost:8000/api/v1） */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

/** 后端根路径（如 http://localhost:8000），由 API_BASE_URL 去掉 /api/v1 得到 */
export const BACKEND_BASE_URL = API_BASE_URL.replace('/api/v1', '')

/** 统一的超时时间设置 (毫秒) */
export const API_TIMEOUT = 10000
export const getBaseUrl = () => {
  // 优先使用 Vite 环境变量，兜底本地开发路径
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
}

// 统一的超时时间设置 (毫秒)
export const API_TIMEOUT = 10000
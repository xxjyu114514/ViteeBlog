export const API_CONFIG = {
  // 基础URL配置
  BASE_URL: {
    development: 'http://127.0.0.1:8000/api/v1',
    production: '/api/v1' // 生产环境使用相对路径
  },
  
  // 认证相关接口
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register', 
    SEND_REGISTER_CODE: '/auth/send-register-code'
  },
  
  // 文章相关接口
  ARTICLE: {
    AUTOSAVE: '/article/autosave',
    DETAIL: '/article/:id', // :id 为占位符
    PUBLISH: '/article/:id/publish',
    PUBLIC_LIST: '/article/public/list',    // 修复路径问题：原为 /article/list
    MY_LIST: '/article/my/list',           // 修复路径问题：原为 /article/user/my-articles
    SOFT_DELETE: '/article/:id',
    RESTORE: '/article/:id/restore'
  },
  
  // 元数据管理接口（分类、标签）
  META: {
    TAGS: '/meta/tags',
    CATEGORIES: '/meta/categories'
  }
}

// 根据环境获取基础URL
export function getBaseUrl() {
  return process.env.NODE_ENV === 'production' 
    ? API_CONFIG.BASE_URL.production 
    : API_CONFIG.BASE_URL.development
}
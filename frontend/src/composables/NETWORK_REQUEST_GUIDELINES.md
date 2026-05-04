# 网络请求编写规范

## 📋 核心原则

### 1. **必须先阅读后端API文档**
- **绝对禁止**在未查看 `README.md` 中API格式的情况下编写网络请求
- 所有API调用必须严格遵循后端返回的实际数据结构
- API文档位置：项目根目录的 `README.md` 文件

### 2. **统一响应格式**
所有API方法必须返回统一格式：
```javascript
// 成功响应
{ success: true, data: responseData }

// 失败响应  
{ success: false, message: '用户友好的错误信息' }
```

### 3. **集中管理原则**
- 所有网络请求必须放在 `src/composables/` 目录
- 按业务模块拆分文件（如 `useAuthAPI.js`, `useArticleAPI.js`）
- **严禁**在页面组件中直接编写 fetch/axios 调用

## 🔧 正确的API封装模板

```javascript
import { createFetch } from '@vueuse/core'
import { useUserStore } from '@/stores/user'
import { getBaseUrl } from '@/config/apiConfig'
import { buildUrl } from '@/utils/apiUtils'

// 1. 创建预配置的fetch实例
const useBaseFetch = createFetch({
  baseUrl: getBaseUrl(),
  options: {
    async beforeFetch({ options }) {
      const userStore = useUserStore()
      if (userStore.token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${userStore.token}`,
        }
      }
      return { options }
    },
    onFetchError(ctx) {
      // 全局错误处理
      if (ctx.response?.status === 401) {
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/login'
      }
      return ctx
    },
  },
})

// 2. 统一的错误信息提取函数
const extractFriendlyErrorMessage = (error, context = '操作') => {
  if (!error) {
    return `${context}失败，请稍后重试`
  }
  
  // 优先使用后端返回的具体错误详情
  if (error.data?.detail) {
    return error.data.detail
  }
  
  // 根据HTTP状态码提供友好提示
  switch (error.status) {
    case 400: return '输入信息有误，请检查后重试'
    case 401: return '身份验证失败，请重新登录'
    case 403: return '权限不足'
    case 404: return '资源不存在或已被删除'
    case 429: return '操作太频繁，请稍后再试'
    case 500: return '系统繁忙，请稍后重试'
    default: return `${context}失败，请稍后重试`
  }
}

// 3. API方法实现模板
export function useYourModuleAPI() {
  // ✅ 正确：直接使用 result.data（根据实际API返回结构）
  const getSomething = async (id) => {
    const url = buildUrl('/your-endpoint/:id', { id })
    const { data, error } = await useBaseFetch(url).get().json()
    
    if (!error.value) {
      // 关键：确认后端API实际返回的数据结构
      // 根据README.md，大多数API直接返回对象，不是 { info: object }
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '获取数据')
    return { success: false, message: errorMessage }
  }

  // ✅ 正确：POST/PUT请求模板
  const createSomething = async (payload) => {
    const { data, error } = await useBaseFetch('/your-endpoint').post(payload).json()
    
    if (!error.value) {
      return { success: true, data: data.value }
    }
    
    const errorMessage = extractFriendlyErrorMessage(error.value, '创建数据')
    return { success: false, message: errorMessage }
  }

  return {
    getSomething,
    createSomething
  }
}
```

## 🚫 常见错误及避免方法

### 错误1：假设错误的数据结构
```javascript
// ❌ 错误：假设返回 { info: data }
const result = await apiCall()
const actualData = result.data.info  // TypeError!

// ✅ 正确：根据API文档确认实际结构
const result = await apiCall()
const actualData = result.data  // 直接使用data
```

### 错误2：未处理undefined情况
```javascript
// ❌ 错误：直接访问可能为undefined的属性
const contentPath = article.content_path

// ✅ 正确：添加安全检查
const contentPath = article?.content_path || ''
```

### 错误3：硬编码URL
```javascript
// ❌ 错误：硬编码完整URL
const response = await fetch('http://127.0.0.1:8000/api/v1/article/1')

// ✅ 正确：使用配置和工具函数
const url = buildUrl('/article/:id', { id: 1 })
const response = await useBaseFetch(url).get()
```

## 🔍 API调试检查清单

在编写任何网络请求前，必须确认：

- [ ] 已阅读 `README.md` 中对应的API文档
- [ ] 确认了请求方法（GET/POST/PUT/DELETE）
- [ ] 确认了请求参数格式和位置（query/body/path）
- [ ] 确认了成功响应的数据结构
- [ ] 确认了可能的错误状态码和错误信息格式
- [ ] 确认了是否需要认证（大多数API需要JWT token）
- [ ] 在浏览器开发者工具中实际测试过该API

## 📊 后端API响应结构参考

根据当前项目API设计，常见响应结构：

### 获取单个资源（GET /resource/:id）
```json
{
  "id": 1,
  "title": "资源标题",
  "content_path": "storage/articles/xxx.md",
  // ... 其他字段
}
```

### 获取列表资源（GET /resource/list）
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pages": 10
}
```

### 创建/更新资源（POST/PUT）
```json
{
  "id": 1,
  "title": "新创建的资源",
  // ... 返回完整对象
}
```

### 操作成功（无数据返回）
```json
{
  "message": "操作成功"
}
```

## 💡 最佳实践

1. **防御性编程**：始终假设网络请求可能失败
2. **类型安全**：在访问嵌套属性前进行存在性检查
3. **错误日志**：在控制台记录原始错误信息便于调试
4. **用户友好**：向用户展示业务语言而非技术错误
5. **一致性**：所有API方法遵循相同的返回格式
6. **文档驱动**：以README.md为唯一真相源

## 🔄 更新维护

- 当后端API发生变化时，必须同步更新前端API封装
- 修改API封装前必须先确认新的API文档
- 保持API封装与后端实际行为的一致性

---
**最后更新**: 2026-05-04  
**维护者**: Frontend Team
# ViteeBlog 项目开发手册

本仓库采用前后端分离架构。`frontend/` 为 Vue3 前端项目，`backend/` 为 FastAPI 后端项目。

## 🚀 后端接口调试指南

后端接口文档地址（服务启动后访问）：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 1. 通用请求规范
* **Base URL**: `http://127.0.0.1:8000/api/v1`
* **Content-Type**: `application/json`
* **鉴权方式**: 采用 JWT。登录成功后获取 `access_token`，后续请求需在 Header 中携带：
  `Authorization: Bearer <Your_Token>`

---

## 🔐 用户认证模块 (Auth) - 重要更新

### ⚡ 核心变化说明

**注册流程已重构为两步验证机制：**
1. 先调用发送验证码接口获取邮箱验证码
2. 注册时必须携带验证码参数

> **注意**：旧的独立验证码校验接口已整合到注册流程中，验证码一次性有效。

---

### 📋 接口清单

#### 1️⃣ 发送注册验证码

**接口地址**: `POST /auth/send-register-code`

**功能说明**: 向指定邮箱发送6位数字验证码，用于用户注册

**请求参数**:
```json
{
  "email": "user@example.com"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | ✅ | 用户邮箱地址，需符合邮箱格式 |

**成功响应** (200 OK):
```json
{
  "message": "验证码已发送至您的邮箱"
}
```

**失败响应**:

❌ **400 Bad Request** - 邮箱已被注册
```json
{
  "detail": "该邮箱已注册，请直接登录"
}
```

❌ **429 Too Many Requests** - 发送过于频繁
```json
{
  "detail": "请在 45秒后重试"
}
```

❌ **500 Internal Server Error** - 服务器错误
```json
{
  "detail": "验证码保存失败: [具体错误信息]"
}
```

**前端注意事项**:
- ✅ 点击发送按钮后立即禁用按钮，开启60秒倒计时
- ✅ 倒计时期间禁止重复请求，避免触发429错误
- ✅ 验证码有效期为10分钟
- ⚠️ 只有未注册的邮箱才能发送注册验证码

---

#### 2️⃣ 用户注册

**接口地址**: `POST /auth/register`

**功能说明**: 使用邮箱验证码完成用户注册

**请求参数**:
```json
{
  "user_in": {
    "username": "BaoZi",
    "email": "user@example.com",
    "password": "123456"
  },
  "email_code": "123456"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| user_in.username | string | ✅ | 3-50字符 | 用户名 |
| user_in.email | string | ✅ | 邮箱格式 | 邮箱地址 |
| user_in.password | string | ✅ | 6-128字符 | 密码 |
| email_code | string | ✅ | 6位数字 | 邮箱验证码 |

**成功响应** (201 Created):
```json
{
  "id": 1,
  "username": "BaoZi",
  "email": "user@example.com",
  "role": "common",
  "created_at": "2026-04-15T20:00:00"
}
```

**失败响应**:

❌ **400 Bad Request** - 验证码错误或已失效
```json
{
  "detail": "验证码错误或已失效"
}
```

❌ **400 Bad Request** - 用户名或邮箱已存在
```json
{
  "detail": "用户名或邮箱已存在"
}
```

❌ **422 Unprocessable Entity** - 参数验证失败
```json
{
  "detail": [
    {
      "loc": ["body", "user_in", "password"],
      "msg": "String should have at least 6 characters",
      "type": "string_too_short"
    }
  ]
}
```

❌ **500 Internal Server Error** - 服务器错误
```json
{
  "detail": "注册失败，请稍后再试"
}
```

**前端注意事项**:
- ✅ 必须先调用 `/send-register-code` 获取验证码
- ✅ 验证码一次性有效，验证后立即销毁
- ✅ 注册成功后可直接跳转到登录页面
- ⚠️ 用户名长度必须在3-50个字符之间
- ⚠️ 密码长度必须在6-128个字符之间

---

#### 3️⃣ 用户登录

**接口地址**: `POST /auth/login`

**功能说明**: 用户使用用户名和密码登录，获取JWT Token

**请求参数**:
```json
{
  "username": "BaoZi",
  "password": "123456"
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码 |

**成功响应** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "BaoZi",
    "email": "user@example.com",
    "role": "common",
    "created_at": "2026-04-15T20:00:00"
  }
}
```

**失败响应**:

❌ **401 Unauthorized** - 用户名或密码错误
```json
{
  "detail": "用户名或密码错误"
}
```

❌ **401 Unauthorized** - 账号被锁定
```json
{
  "detail": "由于连续登录失败，账号已被锁定15分钟"
}
```

❌ **403 Forbidden** - 账号锁定中
```json
{
  "detail": "账号已锁定，请在 12 分钟后再试"
}
```

**前端注意事项**:
- ⚠️ **安全机制**：连续3次登录失败将锁定账号15分钟
- ✅ 登录成功后保存 `access_token` 到 localStorage 或 Pinia Store
- ✅ 后续所有需要鉴权的请求都需在 Header 中携带 Token
- ✅ 可以根据 `user.role` 判断用户权限（`admin` 或 `common`）

---

### 🔑 Token 使用示例

**在请求头中携带 Token**:
```javascript
// Axios 示例
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// 或者针对特定请求
axios.get('/api/v1/articles', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

**Token 有效期**: 60分钟（可在后端 `.env` 中配置 `ACCESS_TOKEN_EXPIRE_MINUTES`）

---

### 🛡️ 安全特性说明

#### 1. 登录保护机制
- **失败计数**：每次登录失败会累加计数
- **自动锁定**：连续3次失败后锁定15分钟
- **自动解锁**：锁定时间过后自动重置计数
- **成功重置**：登录成功后立即清空失败计数

#### 2. 验证码保护机制
- **频率限制**：同一邮箱60秒内只能发送一次验证码
- **有效期**：验证码10分钟后自动过期
- **一次性**：验证码校验通过后立即销毁，防止重放攻击
- **唯一性**：新验证码生成时会标记旧验证码为已删除

#### 3. 密码安全
- **加密存储**：使用 bcrypt 算法哈希存储
- **长度限制**：最少6位，最多128位
- **传输安全**：建议使用 HTTPS（生产环境）

---

### 📝 完整注册流程示例

```javascript
// Step 1: 发送验证码
async function sendVerificationCode(email) {
  try {
    const response = await axios.post('/api/v1/auth/send-register-code', {
      email: email
    })
    
    // 开启60秒倒计时
    startCountdown(60)
    
    return response.data
  } catch (error) {
    if (error.response?.status === 429) {
      // 提取剩余秒数
      const seconds = error.response.data.detail.match(/\d+/)[0]
      startCountdown(seconds)
    }
    throw error
  }
}

// Step 2: 完成注册
async function register(username, email, password, code) {
  try {
    const response = await axios.post('/api/v1/auth/register', {
      user_in: {
        username: username,
        email: email,
        password: password
      },
      email_code: code
    })
    
    // 注册成功，跳转到登录页
    router.push('/login')
    
    return response.data
  } catch (error) {
    // 显示错误提示
    ElMessage.error(error.response?.data?.detail || '注册失败')
    throw error
  }
}

// Step 3: 登录
async function login(username, password) {
  try {
    const response = await axios.post('/api/v1/auth/login', {
      username: username,
      password: password
    })
    
    // 保存 Token 和用户信息
    const { access_token, user } = response.data
    localStorage.setItem('token', access_token)
    useUserStore().setUser(user)
    
    // 跳转到首页
    router.push('/')
    
    return response.data
  } catch (error) {
    if (error.response?.status === 403) {
      // 账号被锁定
      ElMessage.warning(error.response.data.detail)
    } else {
      ElMessage.error('登录失败')
    }
    throw error
  }
}
```

---

### ⚠️ 前端开发避坑指南

#### 常见错误处理

| 状态码 | 含义 | 前端处理建议 |
|--------|------|-------------|
| 400 | 请求参数错误 | 显示具体错误信息，引导用户修正 |
| 401 | 认证失败 | 清除本地 Token，跳转登录页 |
| 403 | 账号被锁定 | 显示剩余锁定时间，禁用登录按钮 |
| 422 | 参数验证失败 | 显示字段级别的错误提示 |
| 429 | 请求过于频繁 | 显示倒计时，禁用发送按钮 |
| 500 | 服务器错误 | 显示友好提示，建议稍后重试 |

#### 最佳实践

1. **验证码倒计时**
   ```javascript
   // 使用 ref 管理倒计时状态
   const countdown = ref(0)
   const canSendCode = computed(() => countdown.value === 0)
   
   function startCountdown(seconds) {
     countdown.value = seconds
     const timer = setInterval(() => {
       countdown.value--
       if (countdown.value <= 0) {
         clearInterval(timer)
       }
     }, 1000)
   }
   ```

2. **表单验证**
   ```javascript
   // 使用 Element Plus 表单验证规则
   const rules = {
     username: [
       { required: true, message: '请输入用户名', trigger: 'blur' },
       { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
     ],
     email: [
       { required: true, message: '请输入邮箱', trigger: 'blur' },
       { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
     ],
     password: [
       { required: true, message: '请输入密码', trigger: 'blur' },
       { min: 6, max: 128, message: '密码长度为6-128个字符', trigger: 'blur' }
     ],
     code: [
       { required: true, message: '请输入验证码', trigger: 'blur' },
       { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
     ]
   }
   ```

3. **Token 刷新策略**
   ```javascript
   // 拦截器中处理 Token 过期
   axios.interceptors.response.use(
     response => response,
     error => {
       if (error.response?.status === 401) {
         // Token 过期，清除本地数据并跳转登录
         localStorage.removeItem('token')
         useUserStore().clearUser()
         router.push('/login')
       }
       return Promise.reject(error)
     }
   )
   ```

---

### 📊 用户角色说明

| 角色 | 值 | 说明 |
|------|-----|------|
| 普通用户 | `common` | 默认角色，可以浏览、评论、留言 |
| 管理员 | `admin` | 博主角色，拥有文章管理、评论审核等权限 |

---

### 🔄 后续更新计划

- [ ] 密码重置功能（通过邮箱验证码）
- [ ] 邮箱绑定/解绑功能
- [ ] Token 自动刷新机制
- [ ] 第三方登录支持

---

**最后更新时间**: 2026-04-15  
**文档版本**: v2.0  
**维护者**: Backend Team

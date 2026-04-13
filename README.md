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

### 2. 核心接口契约 (前端调用必看)

#### A. 用户认证模块 (Auth)
| 功能 | 路径 | 方法 | 关键说明 |
| :--- | :--- | :--- | :--- |
| **注册** | `/auth/register` | `POST` | 需包含 `username`, `email`, `password` |
| **登录** | `/auth/login` | `POST` | 失败 3 次锁定 15 分钟。成功返回 `access_token` 和用户信息 |

**登录成功返回示例：**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin", // admin 为博主，common 为普通用户
    "id": 1,
    "created_at": "2024-05-20T10:00:00"
  }
}

## 🔐 身份验证与安全校验流

验证码接口并非独立功能，它必须配合以下两个业务场景使用：

### 场景 A：修改/重置密码 (Reset Password)
1.  **请求码**: 调用 `/send-code`，后端向注册邮箱发码。
2.  **校验码**: 调用 `/verify-code`。
    - **成功**: 后端在数据库标记该用户当前 Session 为“已验证”。
    - **下一步**: 前端跳转到修改密码页面，调用 `/reset-password`。

### 场景 B：账号激活/核心操作二次验证
- 涉及到敏感操作（如注销账号）时，前端需先引导用户完成 `/verify-code`。

---

### 🚀 接口规范详解

#### 1. 发送验证码 `POST /auth/send-code`
* **用途**: 触发邮件发送。
* **限制**: 同一邮箱 60 秒内只能调用一次（否则返回 `429`）。

#### 2. 校验验证码 `POST /auth/verify-code`
* **用途**: 验证用户输入的 6 位数是否正确。
* **输入**: 
    ```json
    { "email": "xxx@qq.com", "code": "123456" }
    ```
* **输出**: 
    - `200 OK`: 验证通过。此时前端应在本地状态机标记 `isVerified: true`。
    - `400 Bad Request`: 验证码错误或过期。

---

### ⚠️ 给前端队友的避坑指南
1.  **倒计时逻辑**: 请在发送按钮点击后禁用按钮并开启 60s 倒计时，防止触发后端的 `429` 频率限制。
2.  **自动清空**: 验证码一旦校验成功即刻失效，请勿重复调用 `/verify-code`。
3.  **错误提示**: 
    - 若收到 `404`，提示用户：“该邮箱未注册”。
    - 若收到 `429`，提示用户：“请求太频繁，请稍后再试”。

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

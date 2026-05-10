#  存放登录、注册、用户信息 Schema
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from models.blog_models import UserRole


# 基础模型，包含通用字段
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="电子邮箱")


# 注册请求模型
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="密码")


# 登录请求模型
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# 返回给前端的用户信息模型（隐藏敏感数据）
class UserOut(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    # Pydantic 2.0 的配置写法，允许从 ORM 对象转换
    model_config = ConfigDict(from_attributes=True)


# Token 返回模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# Token 载荷模型（内部校验用）
class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

# 验证码发送请求
class EmailCodeRequest(BaseModel):
    email: EmailStr

# 验证码校验请求
class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=128, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="用于接收验证码的邮箱")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
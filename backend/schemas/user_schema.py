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
    avatar: Optional[str] = None

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


class ProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="新昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, max_length=200, description="个人简介")


class UserProfileOut(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    following_count: int = 0
    followers_count: int = 0
    is_following: bool = False
    created_at: datetime
    
    # 统计字段
    total_articles: int = 0              # 文章总数
    total_likes_received: int = 0        # 收到的总点赞数
    total_views: int = 0                 # 总阅读量
    total_favorites: int = 0             # 文章被收藏的总次数
    total_comments: int = 0              # 文章收到的总评论数
    last_active_at: Optional[datetime] = None  # 最后活跃时间
    
    model_config = ConfigDict(from_attributes=True)


class UserAdminOut(BaseModel):
    """管理员视角的用户信息（含更多字段）"""
    id: int
    username: str
    email: str
    role: UserRole
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    login_attempts: int = 0
    following_count: int = 0
    followers_count: int = 0
    created_at: datetime
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ArticleSimpleOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
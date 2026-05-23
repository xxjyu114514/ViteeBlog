from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class UserSocialOut(BaseModel):
    id: int
    username: str = Field(..., description="用户名")
    avatar: Optional[str] = Field(None, description="头像路径")
    following_count: int = Field(0, description="关注数")
    followers_count: int = Field(0, description="粉丝数")
    # 这个字段对前端 UI 极其重要，建议保留
    is_following: bool = Field(False, description="当前登录用户是否已关注此人")
    
    model_config = ConfigDict(from_attributes=True)

class SocialPaginationOut(BaseModel):
    total: int = Field(..., description="总条数")
    items: List[UserSocialOut] = Field(..., description="用户列表数据")
    
    model_config = ConfigDict(from_attributes=True)

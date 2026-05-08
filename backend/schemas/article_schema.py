from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from models.blog_models import ArticleStatus


class ArticleCreate(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    content: Optional[str] = Field(None, description="文章内容（Markdown格式）")
    content_path: Optional[str] = Field(None, description="Markdown文件存储路径（已废弃，内容直接存储在数据库）")
    category_id: Optional[int] = Field(None, description="所属分类ID")
    tag_ids: List[int] = Field(default=[], description="关联的标签ID列表")
    content_hash: Optional[str] = Field(None, description="内容哈希校验值")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    version: Optional[int] = Field(None, description="版本号（用于乐观锁校验）")


class ArticleReviewAction(BaseModel):
    """管理员审核操作"""
    pass_audit: bool = Field(..., description="True为通过，False为驳回")
    remark: Optional[str] = Field(None, max_length=500, description="驳回理由")


class CategorySimpleOut(BaseModel):
    """分类简化输出"""
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TagSimpleOut(BaseModel):
    """标签简化输出"""
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserSimpleOut(BaseModel):
    """用户简化输出"""
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class ArticleDetailOut(BaseModel):
    """文章详情输出"""
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    content_path: Optional[str] = None
    content_hash: Optional[str] = None
    cover_image: Optional[str] = None
    version: int
    view_count: int
    status: ArticleStatus
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    review_remark: Optional[str] = None
    user_id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # 关联对象
    author: Optional[UserSimpleOut] = None
    category: Optional[CategorySimpleOut] = None
    tags: List[TagSimpleOut] = []
    
    model_config = ConfigDict(from_attributes=True)
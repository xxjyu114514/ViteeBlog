from pydantic import BaseModel, Field
from typing import List, Optional
from models.blog_models import ArticleStatus

class ArticleCreate(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, description="文章内容（Markdown格式）")
    content_path: Optional[str] = Field(None, description="Markdown文件存储路径（可选，如果提供content则自动生成）")
    category_id: int = Field(..., description="所属分类ID")
    tag_ids: List[int] = Field(default=[], description="关联的标签ID列表")
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT)

class ArticleReviewAction(BaseModel):
    """管理员审核操作"""
    pass_audit: bool = Field(..., description="True为通过，False为驳回")
    remark: Optional[str] = Field(None, max_length=500, description="驳回理由（驳回时必填）")
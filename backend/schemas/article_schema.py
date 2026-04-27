from pydantic import BaseModel, Field
from typing import List, Optional
from models.blog_models import ArticleStatus

class ArticleCreate(BaseModel):
    # id 为可选，新建文章时不传，修改文章时必须传
    id: Optional[int] = None

    # 修改点：标题改为 Optional，但保留长度限制
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")

    # 摘要可选
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")

    # 文章正文存储路径或内容
    content: Optional[str] = Field(None, description="文章内容（Markdown格式）")
    content_path: Optional[str] = Field(None, description="Markdown文件存储路径")

    # 修改点：分类ID改为可选
    category_id: Optional[int] = Field(None, description="所属分类ID")

    # 标签ID列表
    tag_ids: List[int] = Field(default=[], description="关联的标签ID列表")

    # 状态
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT, description="文章状态")

    # 修改点：显式保留 content_hash
    content_hash: Optional[str] = Field(None, description="内容哈希校验值")

class ArticleReviewAction(BaseModel):
    """管理员审核操作"""
    pass_audit: bool = Field(..., description="True为通过，False为驳回")
    remark: Optional[str] = Field(None, max_length=500, description="驳回理由")
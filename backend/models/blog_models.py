import enum
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean, Table, Column, Enum,DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime


# 定义枚举类型，增强数据完整性
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMMON = "common"


class ArticleStatus(str, enum.Enum):
    PUBLISHED = "published"
    DRAFT = "draft"


class EditorType(str, enum.Enum):
    MARKDOWN = "markdown"
    RICHTEXT = "richtext"


# 中间表：文章与标签的多对多关系
article_tag = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("article.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """用户表：支持权限隔离与登录锁定"""
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    password: Mapped[str] = mapped_column(String(255), comment="哈希密码")

    # 使用 Enum 代替 String
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), server_default=UserRole.COMMON.value, comment="角色"
    )

    # 登录锁定逻辑字段
    login_attempts: Mapped[int] = mapped_column(Integer, server_default="0", comment="失败次数")
    last_fail_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后失败时间")

    articles: Mapped[List["Article"]] = relationship(back_populates="author")

    email_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="验证码")
    code_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="验证码过期时间")
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="0", comment="邮箱是否验证")


class Category(Base):
    """分类表：支持两级嵌套"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名称")
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), index=True, comment="父级ID"
    )

    articles: Mapped[List["Article"]] = relationship(back_populates="category")


class Tag(Base):
    """标签表"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="标签名称")

    # 修复：补充反向映射
    articles: Mapped[List["Article"]] = relationship(secondary=article_tag, back_populates="tags")


class Article(Base):
    """文章表：高并发查询优化版"""
    title: Mapped[str] = mapped_column(String(200), index=True, comment="标题")
    summary: Mapped[str] = mapped_column(String(500), comment="摘要")

    # 内容区支持复杂文档 [cite: 13, 27]
    content: Mapped[str] = mapped_column(Text(length=4294967295), comment="源码")
    html_content: Mapped[str] = mapped_column(Text(length=4294967295), comment="渲染HTML")

    # 枚举约束
    editor_type: Mapped[EditorType] = mapped_column(
        Enum(EditorType), server_default=EditorType.MARKDOWN.value, comment="编辑器类型"
    )
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), server_default=ArticleStatus.DRAFT.value, index=True, comment="状态"
    )

    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, server_default="0", index=True, comment="阅读量")

    # 外键与索引优化
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), index=True)

    author: Mapped["User"] = relationship(back_populates="articles")
    category: Mapped[Optional["Category"]] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship(secondary=article_tag, back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class Comment(Base):
    """评论表：支持父子嵌套回复"""
    content: Mapped[str] = mapped_column(Text, comment="内容")
    nickname: Mapped[str] = mapped_column(String(50), comment="昵称")
    email: Mapped[str] = mapped_column(String(100), comment="邮箱")
    is_audited: Mapped[bool] = mapped_column(Boolean, server_default="0", index=True, comment="审核状态")

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), index=True)

    # 修复：实现嵌套评论逻辑
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"), comment="父评论ID")

    article: Mapped["Article"] = relationship(back_populates="comments")
    # 自关联：用于查询子回复
    replies: Mapped[List["Comment"]] = relationship("Comment", backref="parent", remote_side="Comment.id")


class Message(Base):
    """留言板表"""
    nickname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    reply_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="博主回复")
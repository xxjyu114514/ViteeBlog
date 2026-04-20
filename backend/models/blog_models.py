import enum
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean, Table, Column, Enum, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime


# 定义枚举类型
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
    password: Mapped[str] = mapped_column(String(255), comment="加密哈希密码")

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), server_default="common", comment="用户角色")

    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像路径")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="1", comment="激活状态")
    login_attempts: Mapped[int] = mapped_column(Integer, server_default="0", comment="失败尝试次数")
    last_fail_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="上次失败时间")

    articles: Mapped[List["Article"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Article(Base):
    """文章表：存储路径与基础信息"""
    title: Mapped[str] = mapped_column(String(200), index=True, comment="标题")
    summary: Mapped[str] = mapped_column(String(500), comment="摘要")
    content_path: Mapped[str] = mapped_column(String(255), comment="Markdown文件物理路径")

    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="文章封面图")
    view_count: Mapped[int] = mapped_column(Integer, server_default="0", comment="阅读量")
    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), server_default="draft", comment="状态")

    # 方案 A 核心字段
    is_audited: Mapped[bool] = mapped_column(Boolean, server_default="0", index=True, comment="是否已审核")

    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="发布时间")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="软删除时间")

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), index=True)

    author: Mapped["User"] = relationship(back_populates="articles")
    category: Mapped[Optional["Category"]] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship(secondary=article_tag, back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class Category(Base):
    """分类表"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名称")
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("category.id", ondelete="SET NULL"), index=True
    )
    articles: Mapped[List["Article"]] = relationship(back_populates="category")


class Tag(Base):
    """标签表"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="标签名称")
    articles: Mapped[List["Article"]] = relationship(secondary=article_tag, back_populates="tags")


class Comment(Base):
    """评论表"""
    content: Mapped[str] = mapped_column(Text)
    nickname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    is_audited: Mapped[bool] = mapped_column(Boolean, server_default="0", index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"))
    article: Mapped["Article"] = relationship(back_populates="comments")
    replies: Mapped[List["Comment"]] = relationship("Comment", backref="parent", remote_side="Comment.id")


class Message(Base):
    """留言板"""
    nickname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    reply_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class VerificationCode(Base):
    """验证码"""
    __tablename__ = "verification_codes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    code: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
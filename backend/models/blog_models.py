import enum
from typing import List , Optional
import sqlalchemy as sa
from sqlalchemy import String, Text, ForeignKey, Integer, Boolean, Table, Column, Enum, DateTime, text, func, \
    UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMMON = "common"


class ArticleStatus(str, enum.Enum):
    PUBLISHED = "published"
    DRAFT = "draft"
    PENDING = "pending"


article_tag = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("article.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """用户表：支持权限隔离、登录锁定与社交关注"""
    __tablename__ = "user"
    
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="邮箱")
    password: Mapped[str] = mapped_column(String(255), comment="加密哈希密码")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), server_default="common", comment="用户角色")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="头像路径")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="1", comment="激活状态")
    login_attempts: Mapped[int] = mapped_column(Integer, server_default="0", comment="失败尝试次数")
    last_fail_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="上次失败时间")

    # 社交关注统计字段
    following_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0, comment="关注数")
    followers_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0, comment="粉丝数")

    articles: Mapped[List["Article"]] = relationship(back_populates="author", cascade="all, delete-orphan",
                                                     foreign_keys="Article.user_id")
    comment_likes: Mapped[List["CommentLike"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    # 社交关注关系映射
    following_relations: Mapped[List["UserFollow"]] = relationship(
        "UserFollow", foreign_keys="UserFollow.follower_id", back_populates="follower", cascade="all, delete-orphan"
    )
    follower_relations: Mapped[List["UserFollow"]] = relationship(
        "UserFollow", foreign_keys="UserFollow.followed_id", back_populates="followed", cascade="all, delete-orphan"
    )


class Article(Base):
    """文章表：升级审核逻辑"""
    __tablename__ = "article"
    __table_args__ = (
        sa.Index('ix_article_category_id', 'category_id'),
        sa.Index('ix_article_user_id', 'user_id'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    summary: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="文章正文内容（Markdown 格式）")
    content_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="封面图片URL")
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="阅读量")
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", comment="是否置顶")
    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), default=ArticleStatus.DRAFT,
                                                  server_default="draft")
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="提交审核时间")
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="审核完成时间")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="发布时间")
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), comment="审核人ID")
    review_remark: Mapped[Optional[str]] = mapped_column(String(500), comment="驳回理由")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    author: Mapped["User"] = relationship(back_populates="articles", foreign_keys=[user_id])
    reviewer: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by])
    category: Mapped[Optional["Category"]] = relationship(back_populates="articles")
    tags: Mapped[List["Tag"]] = relationship(secondary=article_tag, back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    favorites: Mapped[List["ArticleFavorite"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    likes: Mapped[List["ArticleLike"]] = relationship(back_populates="article", cascade="all, delete-orphan")

    like_count: int = 0
    is_liked: bool = False


class ArticleFavorite(Base):
    """文章收藏表"""
    __tablename__ = "article_favorite"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship()
    article: Mapped["Article"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="uq_user_article_favorite"),
    )


class Category(Base):
    """分类表"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="分类名称")
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"), index=True)
    articles: Mapped[List["Article"]] = relationship(back_populates="category")


class Tag(Base):
    """标签表"""
    name: Mapped[str] = mapped_column(String(50), unique=True, comment="标签名称")
    articles: Mapped[List["Article"]] = relationship(secondary=article_tag, back_populates="tags")


class Comment(Base):
    """评论表：支持多级嵌套与后审模式"""
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, comment="评论内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"), index=True)
    is_audited: Mapped[bool] = mapped_column(Boolean, server_default="1", index=True)

    author: Mapped["User"] = relationship(foreign_keys=[user_id])
    article: Mapped["Article"] = relationship(back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id], back_populates="replies")
    replies: Mapped[List["Comment"]] = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    likes: Mapped[List["CommentLike"]] = relationship(back_populates="comment", cascade="all, delete-orphan")

    like_count: int = 0
    is_liked: bool = False


class CommentLike(Base):
    """评论点赞表"""
    __tablename__ = "comment_like"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    comment: Mapped["Comment"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="comment_likes")

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_comment_user_like"),
    )


class ArticleLike(Base):
    """文章点赞表"""
    __tablename__ = "article_like"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    article: Mapped["Article"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("article_id", "user_id", name="uq_article_user_like"),
    )


class CommentReport(Base):
    """评论举报表"""
    __tablename__ = "comment_report"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comment.id", ondelete="CASCADE"), index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(200), comment="举报原因")
    is_resolved: Mapped[bool] = mapped_column(Boolean, server_default="0", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    comment: Mapped["Comment"] = relationship()
    reporter: Mapped["User"] = relationship()


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
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"),
                                                 onupdate=text("CURRENT_TIMESTAMP"))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class UserFollow(Base):
    """用户关注关系表"""
    __tablename__ = "user_follow"
    
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, comment="关注者ID")
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, comment="被关注者ID")
    
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="following_relations")
    followed: Mapped["User"] = relationship("User", foreign_keys=[followed_id], back_populates="follower_relations")
    
    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uq_user_follow"),
    )


# ==============================================================================
# 频道广场系统核心模型
# ==============================================================================

class Channel(Base):
    """频道表：只有管理员可增删改。目前全员开放，仅预留权限字段"""
    __tablename__ = "channel"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="频道名称")
    
    # 已自动继承并复用 Base 类自带的 created_at/updated_at 时间字段，不进行重复定义

    # 允许访问的用户ID列表(预留)，使用原生 list 避免 typing.List 命名冲突
    allowed_user_ids: Mapped[Optional[list]] = mapped_column(sa.JSON, nullable=True, comment="允许访问的用户ID列表(预留)")

    # 关系映射：一个频道包含多条留言，使用小写 list 避免与 typing.List 冲突
    messages: Mapped[list["ChannelMessage"]] = relationship("ChannelMessage", back_populates="channel", cascade="all, delete-orphan")


class ChannelMessage(Base):
    """频道留言表：绝对扁平的时序流，支持媒体附件、单级引用与撤回"""
    __tablename__ = "channel_message"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id", ondelete="CASCADE"), index=True, comment="所属频道ID")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True, comment="发言人ID")
    
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="留言文本内容")
    
    # 动态支持图片、视频等多媒体列表，使用原生 list 对应 JSON 数组
    media_attachments: Mapped[Optional[list]] = mapped_column(sa.JSON, nullable=True, comment="媒体附件列表")
    
    # 扁平流下的单级引用（自关联，上一条被引用的留言ID）
    quote_message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("channel_message.id", ondelete="SET NULL"), nullable=True, index=True, comment="引用的上一条留言ID")
    
    # 已自动继承并复用 Base 类自带的 created_at 字段
    
    # 撤回功能时间戳（取代物理删除）
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="撤回时间(若不为空则代表已被撤回)")

    # 关系映射
    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")
    
    # 单向查询：显式指定 foreign_keys，防止多外键引发的 AmbiguousForeignKeyError 报错
    sender: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    
    # 自关联关系：获取引用的上一条留言，使用 remote_side 指定本地主键
    quoted_message: Mapped[Optional["ChannelMessage"]] = relationship(
        "ChannelMessage", 
        remote_side=[id], 
        foreign_keys=[quote_message_id]
    )

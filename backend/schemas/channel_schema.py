from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Literal, List
from datetime import datetime


# ==============================================================================
# 基础公共数据 Schema（全面拥抱 Pydantic V2 规范）
# ==============================================================================

class UserSimpleOut(BaseModel):
    """用户简要信息输出（频道系统专用，包含头像）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    avatar: Optional[str] = None


class MediaAttachment(BaseModel):
    """媒体附件校验模型：加入特定安全白名单前缀校验"""
    model_config = ConfigDict(from_attributes=True)

    type: Literal["image", "video", "file"] = Field(
        ..., 
        description="媒体类型：image / video / file",
        json_schema_extra={"examples": ["image"]}
    )
    url: str = Field(
        ..., 
        min_length=1,
        description="媒体资源的有效URL地址、本地指定存储路径或Base64数据串"
    )

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        v_strip = v.strip() if isinstance(v, str) else ""
        if not v_strip:
            raise ValueError('媒体资源路径或 URL 不能为空')
            
        # 严格限制白名单安全前缀，禁止任意 '/' 开头的系统路径或 './' 相对路径遍历
        safe_prefixes = ('http://', 'https://', '/storage/', 'data:')
        if any(v_strip.startswith(p) for p in safe_prefixes):
            return v_strip
            
        raise ValueError('URL 格式不合法。仅支持标准的网络 HTTP/HTTPS 地址、/storage/ 本地多媒体路径或 data: base64 数据流')


# ==============================================================================
# 频道相关 Schema
# ==============================================================================

class ChannelCreate(BaseModel):
    """创建频道请求"""
    name: str = Field(..., min_length=2, max_length=50, description="频道名称")


class ChannelUpdateName(BaseModel):
    """更新频道名称请求"""
    name: str = Field(..., min_length=2, max_length=50, description="新频道名称")


class ChannelResponse(BaseModel):
    """频道响应数据"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    created_at: datetime  # 映射自 Base 类的公共属性
    allowed_user_ids: Optional[List[int]] = None  # 与模型层的 JSON 数组无缝映射


# ==============================================================================
# 核心留言相关 Schema
# ==============================================================================

class MessageCreate(BaseModel):
    """创建留言请求：内置组合互斥校验，防止发送空气消息"""
    content: Optional[str] = Field(None, max_length=2000, description="文本留言内容")
    media_attachments: Optional[List[MediaAttachment]] = Field(None, description="支持上传并保存多个多媒体附件")
    quote_message_id: Optional[int] = Field(None, description="引用的上一条留言ID")

    # 核心漏洞修复：Pydantic V2 类级别组合验证器
    @model_validator(mode='after')
    def check_content_or_attachment(self) -> 'MessageCreate':
        # 终极状态校准：前置将 content 字段彻底洗干净，消除检验前后的"多状态隐患"
        if isinstance(self.content, str):
            content_strip = self.content.strip()
            self.content = content_strip if content_strip else None
        else:
            self.content = None
        
        # 此时判定逻辑变得极其干净、可预期
        has_content = self.content is not None
        has_attachments = self.media_attachments is not None and len(self.media_attachments) > 0
        
        if not has_content and not has_attachments:
            raise ValueError("发送消息失败：文本内容与媒体附件不能同时为空！")
            
        return self


class QuotedMessageOut(BaseModel):
    """增强版引用消息输出模型：用于提供安全可靠的引用上下文数据流"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    content: Optional[str]
    user_id: int
    created_at: datetime        # 引用消息的原始创建时间
    sender: UserSimpleOut       # 引用消息发送者简要数据


class MessageResponse(BaseModel):
    """留言响应数据"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    channel_id: int
    user_id: int
    content: Optional[str]
    media_attachments: Optional[List[MediaAttachment]] = None
    created_at: datetime        # 映射自 Base 类的公共属性
    sender: UserSimpleOut
    
    quote_message_id: Optional[int] = None
    quoted_message: Optional[QuotedMessageOut] = None


class WithdrawnContentResponse(BaseModel):
    """用户撤回内容'重新编辑'反填输入框专用 Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    content: Optional[str]
    media_attachments: Optional[List[MediaAttachment]] = None


class MessageStreamResponse(BaseModel):
    """留言流式分页响应数据"""
    items: List[MessageResponse]
    has_more: bool = Field(..., description="是否还有更多历史消息")
    next_cursor: Optional[int] = Field(None, description="下一页的游标ID（传入 before_id 参数）")

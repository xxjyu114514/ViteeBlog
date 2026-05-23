from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional

# ==============================================================================
# 核心组件导入（完全遵照你项目的真实路径）
# ==============================================================================
from dependencies import get_db, get_current_user
from models.blog_models import Channel, ChannelMessage, User, UserRole
from schemas.channel_schema import (
    ChannelCreate, ChannelResponse, ChannelUpdateName,
    MessageCreate, MessageResponse, WithdrawnContentResponse,
    MessageStreamResponse  # 引入分页包装协议
)

router = APIRouter(prefix="", tags=["频道广场聊天系统"])

# ==============================================================================
# 依赖项：严格的管理员权限拦截器
# ==============================================================================
async def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """验证当前登录用户是否为管理员"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="权限不足！只有系统管理员可以操作此接口"
        )
    return current_user


# ==============================================================================
# 1. 频道管理接口 (仅限管理员配置)
# ==============================================================================

@router.post("/channels", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_in: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """【管理员】创建全新的讨论频道广场"""
    stmt = select(Channel).where(Channel.name == channel_in.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该频道名称已存在")
        
    db_channel = Channel(name=channel_in.name)
    db.add(db_channel)
    await db.commit()
    await db.refresh(db_channel)
    return db_channel


@router.put("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel_name(
    channel_id: int,
    channel_in: ChannelUpdateName,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """【管理员】修改频道的名称"""
    stmt = select(Channel).where(Channel.id == channel_id)
    result = await db.execute(stmt)
    db_channel = result.scalar_one_or_none()
    if not db_channel:
        raise HTTPException(status_code=404, detail="目标频道不存在")
        
    db_channel.name = channel_in.name
    await db.commit()
    await db.refresh(db_channel)
    return db_channel


@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """【管理员】删除指定频道（成功后统一规范返回 204 No Content）"""
    stmt = select(Channel).where(Channel.id == channel_id)
    result = await db.execute(stmt)
    db_channel = result.scalar_one_or_none()
    if not db_channel:
        raise HTTPException(status_code=404, detail="目标频道不存在")
        
    await db.delete(db_channel)
    await db.commit()


# ==============================================================================
# 2. 核心发言与交互接口（全员开放）
# ==============================================================================

@router.get("/channels", response_model=List[ChannelResponse])
async def list_channels(db: AsyncSession = Depends(get_db)):
    """获取所有公开频道广场列表"""
    stmt = select(Channel).order_by(Channel.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/channels/{channel_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_channel_message(
    channel_id: int,
    message_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    在指定讨论频道内发送发言（支持图文混合、纯视频或单级引用回复）
    """
    # 1. 验证频道存在性
    channel_stmt = select(Channel).where(Channel.id == channel_id)
    channel_res = await db.execute(channel_stmt)
    if not channel_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="目标讨论频道不存在")

    # 2. 验证引用消息存在性
    if message_in.quote_message_id:
        quote_stmt = select(ChannelMessage).where(ChannelMessage.id == message_in.quote_message_id)
        quote_res = await db.execute(quote_stmt)
        if not quote_res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="所引用的消息已被物理删除或不存在")

    # 3. 数据类型转换：将 Pydantic 对象数组转换为原生 Python list[dict]
    attachments_list = (
        [attachment.model_dump() for attachment in message_in.media_attachments]
        if message_in.media_attachments else None
    )

    # 4. 创建消息记录
    db_message = ChannelMessage(
        channel_id=channel_id,
        user_id=current_user.id,
        content=message_in.content,
        media_attachments=attachments_list,
        quote_message_id=message_in.quote_message_id
    )
    db.add(db_message)
    await db.commit()

    # 5. 重新查询并预加载关系数据（这是必要的，因为 refresh 无法加载 relationship）
    stmt = (
        select(ChannelMessage)
        .where(ChannelMessage.id == db_message.id)
        .options(
            selectinload(ChannelMessage.sender),
            selectinload(ChannelMessage.quoted_message).selectinload(ChannelMessage.sender)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/channels/{channel_id}/messages", response_model=MessageStreamResponse)
async def get_channel_message_stream(
    channel_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    流式滚动获取聊天流（实现分页元信息包装，支持无限滚动加载）
    """
    # 核心策略：为了检测是否还有"更多数据"，我们多查 1 条（limit + 1）
    fetch_limit = limit + 1

    query = (
        select(ChannelMessage)
        .where(
            and_(
                ChannelMessage.channel_id == channel_id,
                ChannelMessage.withdrawn_at.is_(None)
            )
        )
        .options(
            selectinload(ChannelMessage.sender),
            selectinload(ChannelMessage.quoted_message).selectinload(ChannelMessage.sender)
        )
        .order_by(ChannelMessage.id.desc())  # 用 ID 倒序拉最新的回来
        .limit(fetch_limit)
    )

    if before_id:
        query = query.where(ChannelMessage.id < before_id)

    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 检查是否有更多历史
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]  # 切掉多查的那一条
        next_cursor = messages[-1].id  # 倒序中的最后一条就是历史更久的那条，作为下次的 before_id
    else:
        next_cursor = None

    # 迎合前端时序流，直接在切片层面反转，内存消耗极低且数据精准
    items = list(reversed(messages))

    return {
        "items": items,
        "has_more": has_more,
        "next_cursor": next_cursor
    }


@router.post("/channels/messages/{message_id}/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_channel_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    【作者本人】撤回消息（2分钟内防越权软删除）
    """
    stmt = select(ChannelMessage).where(ChannelMessage.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    if message.withdrawn_at:
        raise HTTPException(status_code=400, detail="该消息此前已被撤回")
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="越权违规！你只能撤回属于你自己的留言")

    # 使用与数据库 func.now() 一致的本地时间进行比较
    now_local = datetime.now()
    if now_local - message.created_at > timedelta(minutes=2):
        raise HTTPException(status_code=400, detail="发送时间已超过2分钟，系统已锁定，无法撤回")

    message.withdrawn_at = now_local
    await db.commit()
    return {"status": "success", "message": "消息撤回成功", "message_id": message_id}


@router.get("/channels/messages/{message_id}/re-edit", response_model=WithdrawnContentResponse)
async def get_withdrawn_message_for_reedit(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    【作者本人】获取已撤回消息的未清洗原始内容，专供前端一键反填回聊天框输入槽中
    """
    stmt = select(ChannelMessage).where(ChannelMessage.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="该消息不存在")
    if not message.withdrawn_at:
        raise HTTPException(status_code=400, detail="该消息处于正常公开状态，无须进行重新编辑反填")
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无法获取他人撤回的消息内容")

    return message

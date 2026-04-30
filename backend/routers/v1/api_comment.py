import math
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload

from dependencies import get_db, get_current_user, allow_admin_only
from models.blog_models import Comment, CommentReport, Article, User, UserRole
from schemas.comment_schema import CommentCreate, CommentResponse, ReportCreate, ReportResponse

router = APIRouter()


# 1. 发表评论/回复
@router.post("/articles/{article_id}/comments", response_model=CommentResponse)
async def create_comment(
        article_id: int,
        comment_in: CommentCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 校验文章是否存在
    article_res = await db.execute(select(Article).where(Article.id == article_id))
    if not article_res.scalars().first():
        raise HTTPException(status_code=404, detail="文章不存在")

    # 校验父评论
    if comment_in.parent_id:
        parent_res = await db.execute(
            select(Comment).where(and_(Comment.id == comment_in.parent_id, Comment.article_id == article_id))
        )
        if not parent_res.scalars().first():
            raise HTTPException(status_code=400, detail="父评论不存在或不属于该文章")

    new_comment = Comment(
        content=comment_in.content,
        article_id=article_id,
        user_id=user.id,
        parent_id=comment_in.parent_id,
        is_audited=True  # 后审模式，直接可见
    )
    db.add(new_comment)
    await db.commit()
    
    # 重新查询以加载所有关系和字段
    result = await db.execute(
        select(Comment)
        .where(Comment.id == new_comment.id)
        .options(selectinload(Comment.author))
    )
    comment_with_author = result.scalars().first()
    return comment_with_author


# 2. 获取文章评论列表（扁平）
@router.get("/articles/{article_id}/comments", response_model=List[CommentResponse])
async def get_comments(article_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Comment)
        .where(and_(
            Comment.article_id == article_id,
            Comment.is_audited == True,
            Comment.deleted_at == None
        ))
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


# 3. 软删除评论
@router.delete("/{comment_id}")
async def delete_comment(
        comment_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = res.scalars().first()

    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 权限校验：作者或管理员
    if comment.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权删除他人评论")

    comment.deleted_at = datetime.now()
    await db.commit()
    return {"message": "评论已删除"}


# 4. 举报评论
@router.post("/{comment_id}/report")
async def report_comment(
        comment_id: int,
        report_in: ReportCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 1. 校验评论存在
    comment_res = await db.execute(select(Comment).where(Comment.id == comment_id))
    if not comment_res.scalars().first():
        raise HTTPException(status_code=404, detail="被举报评论不存在")

    # 2. 校验重复举报
    dup_res = await db.execute(
        select(CommentReport).where(and_(
            CommentReport.comment_id == comment_id,
            CommentReport.reporter_id == user.id,
            CommentReport.is_resolved == False
        ))
    )
    if dup_res.scalars().first():
        raise HTTPException(status_code=400, detail="您已举报过该评论，请耐心等待处理")

    report = CommentReport(
        comment_id=comment_id,
        reporter_id=user.id,
        reason=report_in.reason
    )
    db.add(report)
    await db.commit()
    return {"message": "举报成功，感谢您的监督"}


# 5. 管理员：获取待处理举报
@router.get("/admin/reports", response_model=List[ReportResponse])
async def list_reports(admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CommentReport)
        .where(CommentReport.is_resolved == False)
        .options(
            selectinload(CommentReport.reporter),
            selectinload(CommentReport.comment).selectinload(Comment.author)
        )
        .order_by(CommentReport.created_at.desc())
    )
    res = await db.execute(stmt)
    return res.scalars().all()


# 6. 管理员：处理举报
@router.put("/admin/reports/{report_id}/resolve")
async def resolve_report(report_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CommentReport).where(CommentReport.id == report_id))
    report = res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    report.is_resolved = True
    await db.commit()
    return {"message": "举报已标记为已处理"}


# 7. 管理员：全站评论巡查
@router.get("/admin/comments/all")
async def get_all_comments_admin(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    stmt = select(Comment).options(selectinload(Comment.author)).order_by(Comment.created_at.desc())

    # 分页逻辑
    total_res = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_res.scalar() or 0

    res = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = res.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": math.ceil(total / size)
    }
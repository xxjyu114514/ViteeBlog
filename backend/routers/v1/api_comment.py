import math
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from dependencies import get_db, get_current_user, get_current_user_optional, allow_admin_only
from models.blog_models import Comment, CommentReport, Article, User, UserRole, CommentLike
from schemas.comment_schema import CommentCreate, CommentResponse, ReportCreate, ReportResponse, LikeResponse

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
        is_audited=True
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

    # 初始化动态字段
    comment_with_author.like_count = 0
    comment_with_author.is_liked = False

    return comment_with_author


# 2. 获取文章评论列表（扁平）
@router.get("/articles/{article_id}/comments", response_model=List[CommentResponse])
async def get_comments(
        article_id: int,
        db: AsyncSession = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    stmt = (
        select(Comment, func.count(CommentLike.id).label("like_count"))
        .outerjoin(CommentLike, Comment.id == CommentLike.comment_id)
        .where(and_(
            Comment.article_id == article_id,
            Comment.is_audited == 1,  # 使用整数1而不是布尔值True，以兼容TINYINT存储
            Comment.deleted_at == None
        ))
        .group_by(Comment.id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )

    res = await db.execute(stmt)
    results = res.all()

    # 如果用户登录，查询该用户点赞过的评论 ID 集合
    liked_ids = set()
    if user:
        like_check = await db.execute(
            select(CommentLike.comment_id).where(CommentLike.user_id == user.id)
        )
        liked_ids = set(like_check.scalars().all())

    final_list = []
    for comment_obj, like_count in results:
        comment_obj.like_count = like_count or 0
        comment_obj.is_liked = comment_obj.id in liked_ids
        final_list.append(comment_obj)

    return final_list


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


# 4. 点赞/取消点赞
@router.post("/{comment_id}/like", response_model=LikeResponse)
async def toggle_like(
        comment_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 检查评论是否存在且未被删除
    comment_res = await db.execute(
        select(Comment).where(
            and_(Comment.id == comment_id, Comment.deleted_at == None)
        )
    )
    comment = comment_res.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # 检查是否已点赞
    like_stmt = select(CommentLike).where(
        and_(CommentLike.comment_id == comment_id, CommentLike.user_id == user.id)
    )
    existing_like = (await db.execute(like_stmt)).scalars().first()

    if existing_like:
        # 取消点赞
        await db.delete(existing_like)
        liked = False
    else:
        # 添加点赞
        try:
            db.add(CommentLike(comment_id=comment_id, user_id=user.id))
            await db.flush()  # 触发唯一约束检查
            liked = True
        except IntegrityError:
            await db.rollback()
            liked = True  # 并发情况下已存在点赞记录

    await db.commit()

    # 返回最新点赞数
    count_res = await db.execute(
        select(func.count(CommentLike.id)).where(CommentLike.comment_id == comment_id)
    )
    return {"liked": liked, "like_count": count_res.scalar() or 0}


# 5. 举报评论
@router.post("/{comment_id}/report")
async def report_comment(
        comment_id: int,
        report_in: ReportCreate,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # 校验评论存在
    comment_res = await db.execute(select(Comment).where(Comment.id == comment_id))
    if not comment_res.scalars().first():
        raise HTTPException(status_code=404, detail="被举报评论不存在")

    # 校验重复举报
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


# 6. 管理员：获取待处理举报（分页）
@router.get("/admin/reports")  # ✅ 删除了错误的 response_model
async def list_reports(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(CommentReport)
        .where(CommentReport.is_resolved == False)
        .options(
            selectinload(CommentReport.reporter),
            selectinload(CommentReport.comment).selectinload(Comment.author)
        )
        .order_by(CommentReport.created_at.desc())
    )

    # 统计总数
    total_res = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_res.scalar() or 0

    # 分页查询
    res = await db.execute(stmt.offset((page - 1) * size).limit(size))

    return {
        "items": res.scalars().all(),
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0
    }


# 7. 管理员：处理举报
@router.put("/admin/reports/{report_id}/resolve")
async def resolve_report(report_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CommentReport).where(CommentReport.id == report_id))
    report = res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    report.is_resolved = True
    await db.commit()
    return {"message": "举报已标记为已处理"}


# 8. 管理员：全站评论巡查（包括已删除的评论）
@router.get("/admin/comments/all")
async def get_all_comments_admin(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    # 管理员可以看到所有评论，包括已删除的
    stmt = select(Comment).options(selectinload(Comment.author)).order_by(Comment.created_at.desc())

    # 分页逻辑
    total_res = await db.execute(select(func.count()).select_from(Comment))
    total = total_res.scalar() or 0

    res = await db.execute(stmt.offset((page - 1) * size).limit(size))
    items = res.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0  # ✅ 统一写法
    }
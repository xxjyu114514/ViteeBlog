from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from dependencies import get_db, get_current_user, allow_admin_only
from models.blog_models import Category, Tag, User

router = APIRouter()


# --- 分类管理 (建议维持管理员权限，保持站点整洁) ---

@router.get("/categories", summary="查看所有分类列表")
async def list_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category))
    return res.scalars().all()


@router.post("/categories", summary="【管理员专用】新建分类")
async def create_category(
        name: str = Body(..., embed=True),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    # 查重逻辑
    exist = await db.execute(select(Category).where(Category.name == name))
    if exist.scalars().first():
        raise HTTPException(status_code=400, detail="该分类名称已存在")

    new_cat = Category(name=name)
    db.add(new_cat)
    await db.commit()
    return new_cat


@router.delete("/categories/{cat_id}", summary="【管理员专用】删除分类")
async def delete_category(cat_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Category).where(Category.id == cat_id))
    await db.commit()
    return {"message": "分类已删除"}


# --- 标签管理 (已更改：普通用户可自定义标签) ---

@router.get("/tags", summary="查看所有标签列表")
async def list_tags(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Tag))
    return res.scalars().all()


@router.post("/tags", summary="【所有用户可用】新建标签")
async def create_tag(
        name: str = Body(..., embed=True),
        user: User = Depends(get_current_user),  # 更改处：只要登录即可创建
        db: AsyncSession = Depends(get_db)
):
    # 1. 查重逻辑（防止数据库出现重复标签字符串）
    exist_res = await db.execute(select(Tag).where(Tag.name == name))
    exist_tag = exist_res.scalars().first()
    if exist_tag:
        # 如果标签已存在，直接返回已有的标签对象，不报错（提升用户体验）
        return exist_tag

    # 2. 创建新标签
    new_tag = Tag(name=name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag


@router.delete("/tags/{tag_id}", summary="【管理员专用】删除标签库条目")
async def delete_tag(tag_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    """
    注意：这里是物理删除标签库里的条目。
    通常只有管理员发现违规标签时才会调用。
    """
    await db.execute(delete(Tag).where(Tag.id == tag_id))
    await db.commit()
    return {"message": "标签已从系统库中移除"}
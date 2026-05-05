from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from dependencies import get_db, get_current_user, allow_admin_only
from models.blog_models import Category, Tag, User, Article, article_tag

router = APIRouter()


# --- 分类管理 (Category) ---

@router.get("/categories", summary="查看所有分类列表")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取全站所有分类，无需登录"""
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
    await db.refresh(new_cat)
    return new_cat


@router.put("/categories/{cat_id}", summary="【管理员专用】修改分类")
async def update_category(
        cat_id: int,
        name: str = Body(..., embed=True),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Category).where(Category.id == cat_id))
    cat = res.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    cat.name = name
    await db.commit()
    return cat


@router.delete("/categories/{cat_id}", summary="【管理员专用】删除分类")
async def delete_category(cat_id: int, admin: User = Depends(allow_admin_only), db: AsyncSession = Depends(get_db)):
    # 级联检查：查询该分类下未删除的文章数量[cite: 11]
    count_res = await db.execute(
        select(func.count(Article.id)).where(Article.category_id == cat_id, Article.deleted_at == None)
    )
    count = count_res.scalar() or 0

    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该分类下有 {count} 篇文章，请先将文章转移至其他分类后再删除"
        )

    await db.execute(delete(Category).where(Category.id == cat_id))
    await db.commit()
    return {"message": "分类已删除"}


# --- 标签管理 (Tag - 增删改查全功能版) ---

@router.get("/tags", summary="【查】查看所有标签列表")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取全站所有标签，用于前端展示和选择"""
    res = await db.execute(select(Tag))
    return res.scalars().all()


@router.post("/tags", summary="【增】新建标签")
async def create_tag(
        name: str = Body(..., embed=True),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    普通用户即可创建新标签。
    如果标签名已存在，则直接返回已有对象，避免报错。
    """
    exist_res = await db.execute(select(Tag).where(Tag.name == name))
    exist_tag = exist_res.scalars().first()
    if exist_tag:
        return exist_tag

    new_tag = Tag(name=name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag


@router.put("/tags/{tag_id}", summary="【改】修改标签名称")
async def update_tag(
        tag_id: int,
        name: str = Body(..., embed=True),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    """
    仅限管理员修改标签名称。
    修改后，所有关联该标签的文章会自动同步显示新名称。
    """
    res = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = res.scalars().first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 检查新名字是否冲突
    conflict_res = await db.execute(select(Tag).where(Tag.name == name))
    if conflict_res.scalars().first():
        raise HTTPException(status_code=400, detail="该标签名称已存在")

    tag.name = name
    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}", summary="【删】从系统库删除标签")
async def delete_tag(
        tag_id: int,
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    """
    仅限管理员删除标签。
    """
    # 先检查是否存在[cite: 11]
    res = await db.execute(select(Tag).where(Tag.id == tag_id))
    if not res.scalars().first():
        raise HTTPException(status_code=404, detail="标签不存在")

    # 关联检查：通过中间表查询该标签下未删除的文章数量[cite: 11]
    count_res = await db.execute(
        select(func.count(Article.id))
        .join(article_tag, Article.id == article_tag.c.article_id)
        .where(article_tag.c.tag_id == tag_id, Article.deleted_at == None)
    )
    count = count_res.scalar() or 0

    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该标签下有 {count} 篇文章正在使用，请先解除关联后再删除"
        )

    await db.execute(delete(Tag).where(Tag.id == tag_id))
    await db.commit()
    return {"message": "标签已从系统中移除"}
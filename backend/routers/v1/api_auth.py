import traceback
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from dependencies import get_db, allow_admin_only
from schemas.user_schema import UserCreate, UserLogin, UserOut, Token, EmailCodeRequest, VerifyCodeRequest
from repository.auth_repo import AuthRepository
from core.security import generate_verification_code
from core.mail import send_email_async
from models.blog_models import User, UserRole

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register(
        user_in: UserCreate,
        email_code: str = Body(..., embed=True, description="邮箱验证码"),
        db: AsyncSession = Depends(get_db)
):
    # 1. 校验并销毁验证码
    try:
        is_valid = await AuthRepository.verify_and_consume_code(db, user_in.email, email_code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误、已失效或已被使用过"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 验证码核销阶段异常: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器核销验证码失败: {type(e).__name__}")

    # 2. 创建用户
    try:
        new_user = await AuthRepository.create_user(db, user_in.model_dump())
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 用户创建阶段异常: {str(e)}")
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册流程中断，数据库保存失败")


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        return await AuthRepository.authenticate_user(db, login_data.username, login_data.password)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 登录接口出现未知异常: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="登录系统暂时不可用")


@router.post("/send-register-code", status_code=status.HTTP_200_OK, summary="发送注册验证码")
async def send_register_code(payload: EmailCodeRequest, db: AsyncSession = Depends(get_db)):
    code = generate_verification_code()

    try:
        await AuthRepository.save_register_code(db, payload.email, code)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 验证码入库失败: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"数据库无法保存验证码记录，请检查后端日志")

    mail_body = f"您的注册验证码为：{code}，请于10分钟内完成注册。"
    try:
        await send_email_async("ViteeBlog 注册验证", payload.email, mail_body)
    except Exception as e:
        print(f"❌ [AuthAPI] 邮件发送服务崩溃: {str(e)}")
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="邮件推送系统异常，请稍后再试")

    return {"message": "验证码已成功发送至您的邮箱，请查收"}


@router.put("/admin/users/{user_id}/role", summary="【超级管理员】修改用户角色")
async def update_user_role(
        user_id: int,
        new_role: UserRole = Body(..., embed=True),
        admin: User = Depends(allow_admin_only),
        db: AsyncSession = Depends(get_db)
):
    # 安全校验 1：不能修改自己的权限
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    # 安全校验 2：目标用户必须存在
    res = await db.execute(select(User).where(User.id == user_id))
    target_user = res.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    # 安全校验 3：降级管理员时，确保全站至少保留一名管理员
    if target_user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        admin_count_res = await db.execute(select(func.count(User.id)).where(User.role == UserRole.ADMIN))
        if admin_count_res.scalar() <= 1:
            raise HTTPException(status_code=400, detail="全站必须至少保留一名管理员")

    # 执行更新
    target_user.role = new_role
    await db.commit()
    return {"message": f"成功将用户角色更新为 {new_role}"}

###
import traceback
import uuid
import os
import aiofiles
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Body, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from dependencies import get_db, allow_admin_only, get_current_user
from schemas.user_schema import (
    UserCreate, UserLogin, UserOut, Token, EmailCodeRequest,
    VerifyCodeRequest, PasswordChange, ForgotPasswordRequest, ResetPasswordRequest,
    ProfileUpdate
)
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


@router.put("/change-password", summary="修改个人密码")
async def change_password(
    pwd_in: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 校验旧密码是否正确
    from core.security import verify_password, get_password_hash
    if not verify_password(pwd_in.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 2. 更新为新密码
    current_user.password = get_password_hash(pwd_in.new_password)
    await db.commit()

    return {"message": "密码修改成功"}


@router.post("/forgot-password/send-code", status_code=status.HTTP_200_OK, summary="发送找回密码验证码")
async def send_password_reset_code(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    code = generate_verification_code()
    try:
        await AuthRepository.save_password_reset_code(db, payload.email, code)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 验证码入库失败: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="数据库无法保存验证码记录")

    mail_body = f"您的密码重置验证码为：{code}，请于10分钟内完成密码重置后登录。如非本人操作，请忽略此邮件。"
    try:
        await send_email_async("ViteeBlog 密码重置", payload.email, mail_body)
    except Exception as e:
        print(f"❌ [AuthAPI] 邮件发送失败: {str(e)}")
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail="邮件推送系统异常，请稍后再试")

    return {"message": "验证码已发送至您的邮箱，请查收"}


@router.post("/forgot-password/reset", summary="验证验证码并重置密码")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # 1. 校验验证码
    try:
        is_valid = await AuthRepository.verify_and_consume_code(db, payload.email, payload.code)
        if not is_valid:
            raise HTTPException(status_code=400, detail="验证码错误、已失效或已被使用过")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 验证码核销异常: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="验证码校验失败")

    # 2. 查找用户并更新密码
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    from core.security import get_password_hash
    user.password = get_password_hash(payload.new_password)
    await db.commit()

    return {"message": "密码重置成功，请使用新密码登录"}


@router.delete("/delete-account", summary="注销个人账号")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 管理员不能注销自己的账号
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="管理员账号不能注销，请先转让管理员权限")

    current_user.is_active = False
    current_user.deleted_at = datetime.now()
    await db.commit()

    return {"message": "账号已注销，感谢您的使用"}


@router.put("/admin/users/{user_id}/restore", summary="【管理员】恢复已注销账号")
async def restore_account(
    user_id: int,
    admin: User = Depends(allow_admin_only),
    db: AsyncSession = Depends(get_db)
):
    # 1. 查找目标用户
    res = await db.execute(select(User).where(User.id == user_id))
    target_user = res.scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 检查该用户是否确实已注销
    if target_user.is_active and target_user.deleted_at is None:
        raise HTTPException(status_code=400, detail="该账号未被注销，无需恢复")

    # 3. 恢复账号
    target_user.is_active = True
    target_user.deleted_at = None
    await db.commit()

    return {"message": f"账号 {target_user.username} 已恢复"}


@router.post("/upload-avatar", summary="上传用户头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 校验文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片文件")

    # 2. 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"avatar_{uuid.uuid4().hex}{ext}"

    # 3. 存储到 storage/avatars/ 目录
    avatar_dir = "storage/avatars"
    os.makedirs(avatar_dir, exist_ok=True)
    file_path = os.path.join(avatar_dir, unique_name)

    # 4. 保存文件
    try:
        content = await file.read()
        if len(content) > 2 * 1024 * 1024:  # 头像限制 2MB
            raise HTTPException(status_code=400, detail="头像大小不能超过2MB")
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
    except Exception:
        raise HTTPException(status_code=500, detail="头像保存失败")

    # 5. 更新用户 avatar 字段
    avatar_url = f"/storage/avatars/{unique_name}"
    current_user.avatar = avatar_url
    await db.commit()

    return {"url": avatar_url, "message": "头像上传成功"}


@router.put("/update-profile", summary="修改个人资料")
async def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. 如果传了 username，检查是否重名
    if profile_in.username:
        existing = await db.execute(
            select(User).where(User.username == profile_in.username, User.id != current_user.id)
        )
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="该昵称已被占用")
        current_user.username = profile_in.username

    # 2. 如果传了 avatar，直接更新
    if profile_in.avatar:
        current_user.avatar = profile_in.avatar

    # 3. 如果传了 bio，直接更新
    if profile_in.bio is not None:
        current_user.bio = profile_in.bio

    await db.commit()
    await db.refresh(current_user)

    return {"message": "个人资料更新成功", "username": current_user.username, "avatar": current_user.avatar}
import traceback
from fastapi import APIRouter, Depends, status, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from schemas.user_schema import UserCreate, UserLogin, UserOut, Token, EmailCodeRequest, VerifyCodeRequest
from repository.auth_repo import AuthRepository
from core.security import generate_verification_code
from core.mail import send_email_async

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register(
        user_in: UserCreate,
        email_code: str = Body(..., embed=True, description="邮箱验证码"),
        db: AsyncSession = Depends(get_db)
):
    """
    企业级注册逻辑：
    1. 强校验验证码（校验后立即销毁）
    2. 校验通过后再创建用户
    """
    # 1. 调用 Repo 中的校验并销毁逻辑
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
        raise HTTPException(
            status_code=500,
            detail=f"服务器核销验证码失败: {type(e).__name__}"
        )

    # 2. 验证码通过，创建用户
    try:
        new_user = await AuthRepository.create_user(db, user_in.model_dump())
        return new_user
    except HTTPException:
        # 允许 Repo 层抛出的 400 (用户已存在等) 直接透传给前端
        raise
    except Exception as e:
        # 捕获未预期的数据库或代码异常
        print(f"❌ [AuthAPI] 用户创建阶段异常: {str(e)}")
        traceback.print_exc()
        await db.rollback()  # 确保发生异常时回滚
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册流程中断，数据库保存失败"
        )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    登录逻辑：由 AuthRepository 处理具体的密码验证和 Token 生成
    """
    try:
        return await AuthRepository.authenticate_user(db, login_data.username, login_data.password)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 登录接口出现未知异常: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="登录系统暂时不可用"
        )


@router.post("/send-register-code", status_code=status.HTTP_200_OK, summary="发送注册验证码")
async def send_register_code(payload: EmailCodeRequest, db: AsyncSession = Depends(get_db)):
    # 1. 临时调试：测试数据库连接和表结构（保留原始调试逻辑）
    try:
        from sqlalchemy import text
        result = await db.execute(text("DESCRIBE verification_codes"))
        columns = result.fetchall()
        print(f"✅ verification_codes 表结构确认成功:")
        for col in columns:
            print(f"   - {col}")
    except Exception as e:
        print(f"❌ [AuthAPI] 表结构自检失败: {e}")
        # 这里不抛出错误，尝试继续运行，因为可能只是权限问题不影响写入

    # 2. 生成验证码
    code = generate_verification_code()

    # 3. 保存验证码到数据库
    try:
        await AuthRepository.save_register_code(db, payload.email, code)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [AuthAPI] 验证码入库失败: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库无法保存验证码记录，请检查后端日志"
        )

    # 4. 异步物理发送邮件
    mail_body = f"您的注册验证码为：{code}，请于10分钟内完成注册。"
    try:
        await send_email_async("ViteeBlog 注册验证", payload.email, mail_body)
    except Exception as e:
        # 邮件发送失败，必须回滚之前存入数据库的验证码，否则会导致用户看到报错但验证码其实已生效
        print(f"❌ [AuthAPI] 邮件发送服务崩溃: {str(e)}")
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件推送系统异常，请稍后再试"
        )

    return {"message": "验证码已成功发送至您的邮箱，请查收"}
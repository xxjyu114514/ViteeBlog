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
    # 调用 Repo 中的校验并销毁逻辑
    is_valid = await AuthRepository.verify_and_consume_code(db, user_in.email, email_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已失效"
        )

    # 验证码通过，创建用户
    try:
        new_user = await AuthRepository.create_user(db, user_in.model_dump())
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后再试"
        )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthRepository.authenticate_user(db, login_data.username, login_data.password)


@router.post("/send-register-code", status_code=status.HTTP_200_OK, summary="发送注册验证码")
async def send_register_code(payload: EmailCodeRequest, db: AsyncSession = Depends(get_db)):
    # 临时调试：测试数据库连接和表结构
    try:
        from sqlalchemy import text
        result = await db.execute(text("DESCRIBE verification_codes"))
        columns = result.fetchall()
        print(f"✅ verification_codes 表结构:")
        for col in columns:
            print(f"   - {col}")
    except Exception as e:
        print(f"❌ 查询表结构失败: {e}")

    code = generate_verification_code()

    # 保存验证码到数据库
    try:
        await AuthRepository.save_register_code(db, payload.email, code)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ 路由层捕获异常: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证码保存失败: {str(e)}"
        )

    # 异步物理发送邮件
    mail_body = f"您的注册验证码为：{code}，请于10分钟内完成注册。"
    try:
        await send_email_async("ViteeBlog 注册验证", payload.email, mail_body)
    except Exception as e:
        # 邮件发送失败，回滚验证码
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件发送失败，请重试"
        )

    return {"message": "验证码已发送至您的邮箱"}


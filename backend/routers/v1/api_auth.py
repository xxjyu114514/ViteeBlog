from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from schemas.user_schema import UserCreate, UserLogin, UserOut, Token, EmailCodeRequest, VerifyCodeRequest
from repository.auth_repo import AuthRepository
from core.security import generate_verification_code
from core.mail import send_email_async  # 确保此模块已按上一步配置好

router = APIRouter()


# --- 注册和登录接口保持不变 ---
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await AuthRepository.create_user(db, user_in.model_dump())
    return new_user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await AuthRepository.authenticate_user(db, login_data.username, login_data.password)
    return result


# --- 修正后的验证码发送接口 (逻辑严密版) ---
@router.post("/send-code", status_code=status.HTTP_200_OK, summary="发送邮箱验证码")
async def send_verification_code(
        payload: EmailCodeRequest,
        db: AsyncSession = Depends(get_db)
):
    code = generate_verification_code()

    # 1. 尝试保存（这里可能会抛出 429 频率限制异常）
    success = await AuthRepository.save_email_code(db, payload.email, code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该邮箱未注册，无法发送验证码"
        )

    # 2. 只有数据库保存成功后，才执行物理发送
    mail_body = f"您的验证码是：{code}，请于10分钟内输入。"
    try:
        await send_email_async("ViteeBlog 验证", payload.email, mail_body)
    except Exception as e:
        # 如果发送失败，虽然数据库存了，但用户收不到，这里报错是严谨的
        raise HTTPException(status_code=500, detail="邮件投递失败")

    return {"message": "验证码已成功保存并发送"}


@router.post("/verify-code", status_code=status.HTTP_200_OK, summary="校验邮箱验证码")
async def verify_code(
        payload: VerifyCodeRequest,
        db: AsyncSession = Depends(get_db)
):
    is_valid = await AuthRepository.verify_email_code(db, payload.email, payload.code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已失效"
        )

    return {"message": "邮箱验证成功"}
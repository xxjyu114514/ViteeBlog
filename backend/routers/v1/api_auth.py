from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from schemas.user_schema import UserCreate, UserLogin, UserOut, Token
from repository.auth_repo import AuthRepository

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    新用户注册接口
    - **username**: 用户名 (唯一)
    - **email**: 邮箱 (唯一)
    - **password**: 密码 (至少6位)
    """
    # 将 Pydantic 模型转为字典传给 repository
    new_user = await AuthRepository.create_user(db, user_in.model_dump())
    return new_user

@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口：支持连续3次失败锁定15分钟
    - **username**: 用户名
    - **password**: 密码
    """
    # 调用 repository 中严谨的校验逻辑
    result = await AuthRepository.authenticate_user(
        db,
        login_data.username,
        login_data.password
    )
    return result
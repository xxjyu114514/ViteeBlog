from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models.blog_models import User, UserRole
from core.security import verify_password, get_password_hash, create_access_token


class AuthRepository:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        """
        严谨的登录验证逻辑：
        1. 检查用户是否存在
        2. 检查锁定状态（15分钟）
        3. 验证密码
        4. 处理失败计数与锁定
        """
        # 1. 查询用户
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        #ououo
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )

        # 2. 检查锁定状态 (需求：连续3次失败锁定15分钟)
        if user.login_attempts >= 3 and user.last_fail_time:
            lock_time = user.last_fail_time + timedelta(minutes=15)
            if datetime.now() < lock_time:
                remaining_time = int((lock_time - datetime.now()).total_seconds() / 60)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"账号已锁定，请在 {remaining_time} 分钟后再试"
                )
            else:
                # 锁定时间已过，重置尝试次数（严谨性：在验证密码前先看是否解除锁定）
                user.login_attempts = 0
                await db.commit()

        # 3. 验证密码
        if not verify_password(password, user.password):
            # 增加失败计数
            user.login_attempts += 1
            user.last_fail_time = datetime.now()
            await db.commit()

            error_msg = "用户名或密码错误"
            if user.login_attempts >= 3:
                error_msg = "由于连续登录失败，账号已被锁定15分钟"

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )

        # 4. 登录成功，重置失败统计
        user.login_attempts = 0
        user.last_fail_time = None
        await db.commit()

        # 5. 生成 Token (包含 ID 和 Role)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        # --- 严谨修复：返回完整的 user 对象以符合 UserOut schema 要求 ---
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user  # 直接返回 user 实例，Pydantic 会自动根据 UserOut 进行过滤和转换
        }

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict):
        """
        严谨的注册逻辑：
        1. 检查唯一性
        2. 密码哈希
        3. 赋予角色
        """
        # 检查用户名和邮箱是否已存在
        query = select(User).where(
            (User.username == user_data['username']) | (User.email == user_data['email'])
        )
        existing_user = (await db.execute(query)).scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或邮箱已存在"
            )

        # 创建新用户对象
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            password=get_password_hash(user_data['password']),
            role=UserRole.COMMON  # 默认注册为普通用户
        )

        db.add(new_user)
        try:
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="注册失败，请稍后再试"
            )
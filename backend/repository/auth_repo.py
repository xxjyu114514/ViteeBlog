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

    @staticmethod
    async def save_email_code(db: AsyncSession, email: str, code: str):
        """
        严谨存储验证码：
        1. 检查距离上次发送是否超过 60 秒
        2. 强制 commit 确保存入磁盘
        """
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            return False

        # --- 逻辑漏洞修复：防止重复/频繁发送 ---
        if user.last_fail_time:  # 借用原字段或单独字段，这里为了严谨建议用过期时间倒推
            # 如果 code_expires_at 存在，且距离过期还有 9 分钟以上（说明刚发过）
            if user.code_expires_at and (user.code_expires_at - datetime.now()).total_seconds() > 540:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="发送太频繁，请 60 秒后再试"
                )

        # 更新验证码信息
        user.email_code = code
        user.code_expires_at = datetime.now() + timedelta(minutes=10)

        # --- 关键修复：必须强制 commit 才能保存到数据库 ---
        try:
            db.add(user)  # 确保对象在 session 中
            await db.commit()  # 提交事务
            await db.refresh(user)  # 刷新状态
            return True
        except Exception as e:
            await db.rollback()
            print(f"数据库保存失败: {e}")
            return False

    @staticmethod
    async def verify_email_code(db: AsyncSession, email: str, code: str):
        """校验并销毁验证码"""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or user.email_code != code:
            return False

        if datetime.now() > user.code_expires_at:
            return False

        # 验证通过，立即失效（防止二次使用）
        user.email_code = None
        user.code_expires_at = None
        await db.commit()
        return True
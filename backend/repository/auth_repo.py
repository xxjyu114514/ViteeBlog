import traceback
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError  # 新增：用于精细捕获 SQL 异常
from fastapi import HTTPException, status
from models.blog_models import User, VerificationCode, UserRole

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
        try:
            # 1. 查询用户
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalars().first()

            if not user:
                # 为了安全，这里可以保持模糊提示，或者根据调试需求改为具体提示
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"登录失败：用户 '{username}' 不存在"
                )

            # 2. 检查锁定状态 (需求：连续3次失败锁定15分钟)
            if user.login_attempts >= 3 and user.last_fail_time:
                lock_time = user.last_fail_time + timedelta(minutes=15)
                if datetime.now() < lock_time:
                    remaining_time = int((lock_time - datetime.now()).total_seconds() / 60)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"由于连续登录失败，账号已锁定，请在 {remaining_time} 分钟后再试"
                    )
                else:
                    # 锁定时间已过，自动重置尝试次数
                    user.login_attempts = 0
                    await db.commit()

                    # 3. 验证密码
            if not verify_password(password, user.password):
                # 增加失败计数
                user.login_attempts += 1
                user.last_fail_time = datetime.now()
                await db.commit()

                attempts_left = 3 - user.login_attempts
                if attempts_left <= 0:
                    detail = "连续失败次数过多，账号已被锁定 15 分钟"
                else:
                    detail = f"用户名或密码错误，您还剩 {attempts_left} 次尝试机会"

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=detail
                )

                # 4. 登录成功，重置失败统计
            user.login_attempts = 0
            user.last_fail_time = None
            await db.commit()

            # 5. 生成 Token (包含 ID 和 Role)
            access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role.value}
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            }

        except HTTPException:
            # 直接抛出已知业务异常
            raise
        except Exception as e:
            # 打印详细堆栈到服务器控制台，方便排查代码 Bug
            print(f"❌ [AuthRepo] 登录流程出现非预期异常: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"服务器内部验证异常，请联系管理员"
            )

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict):
        """
        严谨的注册逻辑：
        1. 检查唯一性
        2. 密码哈希
        3. 赋予角色
        """
        try:
            # 1. 检查用户名和邮箱是否已存在
            query = select(User).where(
                (User.username == user_data['username']) | (User.email == user_data['email'])
            )
            existing_user = (await db.execute(query)).scalars().first()
            if existing_user:
                field = "用户名" if existing_user.username == user_data['username'] else "邮箱"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"注册失败：该{field}已被占用"
                )

                # 2. 创建新用户对象
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=get_password_hash(user_data['password']),
                role=UserRole.COMMON
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            print(f"❌ [AuthRepo] 注册时数据库写入失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库保存用户信息失败，请稍后再试"
            )
        except Exception as e:
            await db.rollback()
            print(f"❌ [AuthRepo] 注册流程未知异常: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册服务暂不可用: {str(e)}"
            )

    @staticmethod
    async def save_register_code(db: AsyncSession, email: str, code: str):
        """企业级预注册逻辑"""
        try:
            # 1. 检查是否已注册
            user_exists = await db.execute(select(User).where(User.email == email))
            if user_exists.scalars().first():
                raise HTTPException(status_code=400, detail="该邮箱已注册，请直接登录")

                # 2. 频率限制与清理旧码：将该邮箱下所有存活的验证码标记为删除（软删除）
            await db.execute(
                update(VerificationCode)
                .where(
                    VerificationCode.email == email,
                    VerificationCode.deleted_at.is_(None)
                )
                .values(deleted_at=datetime.now())
            )

            # 3. 存入新验证码（有效期10分钟）
            new_code = VerificationCode(
                email=email,
                code=code,
                expires_at=datetime.now() + timedelta(minutes=10)
            )

            db.add(new_code)
            await db.commit()
            return True

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            print(f"❌ [AuthRepo] 保存验证码到数据库失败: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"验证码系统异常，暂时无法发送"
            )

    @staticmethod
    async def verify_and_consume_code(db: AsyncSession, email: str, code: str):
        """校验并立即销毁验证码（防止重放攻击）"""
        try:
            result = await db.execute(
                select(VerificationCode)
                .where(
                    VerificationCode.email == email,
                    VerificationCode.code == code,
                    VerificationCode.deleted_at.is_(None)
                )
            )
            record = result.scalars().first()

            if not record:
                return False

            # 检查是否过期
            if datetime.now() > record.expires_at:
                # 软删除过期验证码，防止堆积
                await db.execute(
                    update(VerificationCode)
                    .where(VerificationCode.id == record.id)
                    .values(deleted_at=datetime.now())
                )
                await db.commit()
                return False

                # 校验通过，立即“消耗”掉（软删除），确保该验证码只能使用一次
            await db.execute(
                update(VerificationCode)
                .where(VerificationCode.id == record.id)
                .values(deleted_at=datetime.now())
            )
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            print(f"❌ [AuthRepo] 验证码验证逻辑出错: {str(e)}")
            traceback.print_exc()
            return False
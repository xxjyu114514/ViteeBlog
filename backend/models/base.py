from datetime import datetime
from sqlalchemy import MetaData, func, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # 统一主键
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键ID"
    )

    # 统一时间字段 (建议去掉 timezone=True 以适配标准的 MySQL DATETIME)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(), # 这里 SQLAlchemy 会在更新记录时自动调用此函数
        comment="更新时间"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None, comment="删除时间（软删除）"
    )
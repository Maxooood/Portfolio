from datetime import datetime

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole:
    ADMIN = "admin"
    MANAGER = "manager"
    DISPATCHER = "dispatcher"
    SHIFT_MANAGER = "shift_manager"
    EXECUTOR = "executor"
    PPR_ENGINEER = "ppr_engineer"

    ALL = [ADMIN, MANAGER, DISPATCHER, SHIFT_MANAGER, EXECUTOR, PPR_ENGINEER]


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default=UserRole.EXECUTOR)
    department: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    initiated_requests: Mapped[list] = relationship(
        "Request", foreign_keys="Request.initiator_id", back_populates="initiator", lazy="select"
    )
    assigned_requests: Mapped[list] = relationship(
        "Request", foreign_keys="Request.executor_id", back_populates="executor", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User {self.employee_number} ({self.role})>"

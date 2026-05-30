from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100))
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        nullable=False,
    )

    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} user={self.user_id}>"

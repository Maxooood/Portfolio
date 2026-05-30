from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, default="completion")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        nullable=False,
    )

    request: Mapped["Request"] = relationship("Request", back_populates="reports")
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<Report req={self.request_id} type={self.report_type}>"

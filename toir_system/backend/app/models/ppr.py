from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PprSchedule(Base, TimestampMixin):
    __tablename__ = "ppr_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    generated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    generated_by: Mapped["User"] = relationship("User", foreign_keys=[generated_by_id])
    approved_by: Mapped["User | None"] = relationship("User", foreign_keys=[approved_by_id])
    tasks: Mapped[list["PprTask"]] = relationship("PprTask", back_populates="schedule", lazy="select")

    def __repr__(self) -> str:
        return f"<PprSchedule {self.year}-{self.month:02d}>"


class PprTask(Base, TimestampMixin):
    __tablename__ = "ppr_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("ppr_schedules.id"), nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    norm_id: Mapped[int] = mapped_column(ForeignKey("equipment_norms.id"), nullable=False)
    planned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="planned", nullable=False
    )  # planned/in_progress/completed/overdue/cancelled
    request_id: Mapped[int | None] = mapped_column(ForeignKey("requests.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    schedule: Mapped["PprSchedule"] = relationship("PprSchedule", back_populates="tasks")
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="ppr_tasks")
    norm: Mapped["EquipmentNorm"] = relationship("EquipmentNorm", back_populates="ppr_tasks")
    request: Mapped["Request | None"] = relationship("Request", foreign_keys=[request_id])

    def __repr__(self) -> str:
        return f"<PprTask eq={self.equipment_id} date={self.planned_date.date()}>"

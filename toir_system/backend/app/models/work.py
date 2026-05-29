from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Diagnostic(Base, TimestampMixin):
    __tablename__ = "diagnostics"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    performed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    findings: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(Text)
    estimated_repair_hours: Mapped[float | None] = mapped_column(Float)

    request: Mapped["Request"] = relationship("Request", back_populates="diagnostics")
    performed_by: Mapped["User"] = relationship("User", foreign_keys=[performed_by_id])

    def __repr__(self) -> str:
        return f"<Diagnostic req={self.request_id}>"


class Repair(Base, TimestampMixin):
    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    performed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    work_description: Mapped[str] = mapped_column(Text, nullable=False)
    labor_hours: Mapped[float | None] = mapped_column(Float)
    result: Mapped[str | None] = mapped_column(Text)

    request: Mapped["Request"] = relationship("Request", back_populates="repairs")
    performed_by: Mapped["User"] = relationship("User", foreign_keys=[performed_by_id])
    materials: Mapped[list["RepairMaterial"]] = relationship("RepairMaterial", back_populates="repair", lazy="select")

    def __repr__(self) -> str:
        return f"<Repair req={self.request_id}>"


class RepairMaterial(Base):
    __tablename__ = "repair_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    repair_id: Mapped[int] = mapped_column(ForeignKey("repairs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    cost: Mapped[float | None] = mapped_column(Float)

    repair: Mapped["Repair"] = relationship("Repair", back_populates="materials")

    def __repr__(self) -> str:
        return f"<RepairMaterial {self.name} x{self.quantity}>"

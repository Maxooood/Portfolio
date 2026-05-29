from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EquipmentStatus:
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    BROKEN = "broken"
    DECOMMISSIONED = "decommissioned"


class Equipment(Base, TimestampMixin):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    inventory_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    equipment_type: Mapped[str | None] = mapped_column(String(100))
    location: Mapped[str | None] = mapped_column(String(200))
    department: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    year_of_manufacture: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(30), default=EquipmentStatus.OPERATIONAL, nullable=False
    )

    requests: Mapped[list] = relationship("Request", back_populates="equipment", lazy="select")
    norms: Mapped[list] = relationship("EquipmentNorm", back_populates="equipment", lazy="select")
    ppr_tasks: Mapped[list] = relationship("PprTask", back_populates="equipment", lazy="select")

    def __repr__(self) -> str:
        return f"<Equipment {self.inventory_number}: {self.name}>"


class EquipmentNorm(Base, TimestampMixin):
    __tablename__ = "equipment_norms"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    norm_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # daily/weekly/monthly/quarterly/annual
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="norms")
    ppr_tasks: Mapped[list] = relationship("PprTask", back_populates="norm", lazy="select")

    def __repr__(self) -> str:
        return f"<EquipmentNorm eq={self.equipment_id} type={self.norm_type}>"

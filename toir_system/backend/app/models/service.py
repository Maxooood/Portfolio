from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AuxiliaryService(Base, TimestampMixin):
    __tablename__ = "auxiliary_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requests: Mapped[list] = relationship("Request", back_populates="service", lazy="select")
    routing_rules: Mapped[list] = relationship("RoutingRule", back_populates="service", lazy="select")

    def __repr__(self) -> str:
        return f"<AuxiliaryService {self.name}>"


class RoutingRule(Base, TimestampMixin):
    __tablename__ = "routing_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("auxiliary_services.id"), nullable=False)
    equipment_type: Mapped[str | None] = mapped_column(String(100))
    fault_type_id: Mapped[int | None] = mapped_column(ForeignKey("fault_types.id"), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20))
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    service: Mapped["AuxiliaryService"] = relationship("AuxiliaryService", back_populates="routing_rules")
    fault_type: Mapped["FaultType | None"] = relationship("FaultType", foreign_keys=[fault_type_id])
    executor: Mapped["User | None"] = relationship("User", foreign_keys=[executor_id])

    def __repr__(self) -> str:
        return f"<RoutingRule service={self.service_id}>"

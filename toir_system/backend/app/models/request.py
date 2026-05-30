from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RequestStatus:
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_PARTS = "waiting_parts"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"

    ALL = [NEW, ASSIGNED, IN_PROGRESS, WAITING_PARTS, COMPLETED, CLOSED, CANCELLED]


class RequestPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    ALL = [LOW, MEDIUM, HIGH, CRITICAL]


class RequestType:
    UNPLANNED = "unplanned"
    PPR = "ppr"

    ALL = [UNPLANNED, PPR]


class FaultType(Base, TimestampMixin):
    __tablename__ = "fault_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requests: Mapped[list] = relationship("Request", back_populates="fault_type", lazy="select")

    def __repr__(self) -> str:
        return f"<FaultType {self.name}>"


class Request(Base, TimestampMixin):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    request_type: Mapped[str] = mapped_column(String(30), default=RequestType.UNPLANNED, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default=RequestStatus.NEW, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default=RequestPriority.MEDIUM, nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False)
    fault_type_id: Mapped[int | None] = mapped_column(ForeignKey("fault_types.id"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("auxiliary_services.id"), nullable=True)
    initiator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="requests")
    fault_type: Mapped["FaultType | None"] = relationship("FaultType", back_populates="requests")
    service: Mapped["AuxiliaryService | None"] = relationship("AuxiliaryService", back_populates="requests")
    initiator: Mapped["User"] = relationship("User", foreign_keys=[initiator_id], back_populates="initiated_requests")
    executor: Mapped["User | None"] = relationship("User", foreign_keys=[executor_id], back_populates="assigned_requests")
    status_history: Mapped[list["StatusHistory"]] = relationship("StatusHistory", back_populates="request", lazy="select")
    diagnostics: Mapped[list["Diagnostic"]] = relationship("Diagnostic", back_populates="request", lazy="select")
    repairs: Mapped[list["Repair"]] = relationship("Repair", back_populates="request", lazy="select")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="request", lazy="select")

    def __repr__(self) -> str:
        return f"<Request {self.request_number} [{self.status}]>"


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__('datetime').datetime.now(__import__('datetime').timezone.utc),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(Text)

    request: Mapped["Request"] = relationship("Request", back_populates="status_history")
    changed_by: Mapped["User"] = relationship("User", foreign_keys=[changed_by_id])

    def __repr__(self) -> str:
        return f"<StatusHistory req={self.request_id} {self.old_status}->{self.new_status}>"

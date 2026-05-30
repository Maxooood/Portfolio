from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import UserShort
from app.schemas.equipment import EquipmentRead


class FaultTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class FaultTypeCreate(FaultTypeBase):
    pass


class FaultTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class FaultTypeRead(FaultTypeBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusHistoryRead(BaseModel):
    id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by: Optional[UserShort] = None
    changed_at: datetime
    comment: Optional[str] = None

    model_config = {"from_attributes": True}


class RequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    request_type: str = "unplanned"
    priority: str = "medium"
    equipment_id: int
    fault_type_id: Optional[int] = None
    service_id: Optional[int] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    fault_type_id: Optional[int] = None
    service_id: Optional[int] = None
    executor_id: Optional[int] = None
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    comment: Optional[str] = None


class RequestRead(RequestBase):
    id: int
    request_number: str
    status: str
    initiator_id: int
    executor_id: Optional[int] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    equipment: Optional[EquipmentRead] = None
    initiator: Optional[UserShort] = None
    executor: Optional[UserShort] = None
    fault_type: Optional[FaultTypeRead] = None

    model_config = {"from_attributes": True}


class RequestDetail(RequestRead):
    status_history: List[StatusHistoryRead] = []

    model_config = {"from_attributes": True}

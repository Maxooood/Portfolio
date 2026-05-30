from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.equipment import EquipmentRead, EquipmentNormRead
from app.schemas.user import UserShort


class PprScheduleBase(BaseModel):
    year: int
    month: int


class PprScheduleCreate(PprScheduleBase):
    pass


class PprScheduleRead(PprScheduleBase):
    id: int
    generated_at: datetime
    generated_by_id: int
    is_approved: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    generated_by: Optional[UserShort] = None
    approved_by: Optional[UserShort] = None

    model_config = {"from_attributes": True}


class PprTaskBase(BaseModel):
    schedule_id: int
    equipment_id: int
    norm_id: int
    planned_date: datetime
    status: str = "planned"
    request_id: Optional[int] = None
    notes: Optional[str] = None


class PprTaskCreate(PprTaskBase):
    pass


class PprTaskUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    request_id: Optional[int] = None


class PprTaskRead(PprTaskBase):
    id: int
    created_at: datetime
    equipment: Optional[EquipmentRead] = None
    norm: Optional[EquipmentNormRead] = None

    model_config = {"from_attributes": True}


class GenerateScheduleRequest(BaseModel):
    year: int
    month: int


class PprScheduleWithTasks(PprScheduleRead):
    tasks: List[PprTaskRead] = []

    model_config = {"from_attributes": True}

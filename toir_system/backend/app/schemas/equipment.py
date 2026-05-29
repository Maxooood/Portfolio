from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EquipmentBase(BaseModel):
    name: str
    inventory_number: str
    equipment_type: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    status: str = "operational"


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    inventory_number: Optional[str] = None
    equipment_type: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    status: Optional[str] = None


class EquipmentRead(EquipmentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EquipmentNormBase(BaseModel):
    equipment_id: int
    norm_type: str
    interval_days: int
    description: Optional[str] = None
    is_active: bool = True


class EquipmentNormCreate(EquipmentNormBase):
    pass


class EquipmentNormUpdate(BaseModel):
    norm_type: Optional[str] = None
    interval_days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EquipmentNormRead(EquipmentNormBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

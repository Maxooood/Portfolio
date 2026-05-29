from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuxiliaryServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class AuxiliaryServiceCreate(AuxiliaryServiceBase):
    pass


class AuxiliaryServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AuxiliaryServiceRead(AuxiliaryServiceBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RoutingRuleBase(BaseModel):
    service_id: int
    equipment_type: Optional[str] = None
    fault_type_id: Optional[int] = None
    priority: Optional[str] = None
    executor_id: Optional[int] = None
    order: int = 0
    is_active: bool = True


class RoutingRuleCreate(RoutingRuleBase):
    pass


class RoutingRuleUpdate(BaseModel):
    equipment_type: Optional[str] = None
    fault_type_id: Optional[int] = None
    priority: Optional[str] = None
    executor_id: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class RoutingRuleRead(RoutingRuleBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

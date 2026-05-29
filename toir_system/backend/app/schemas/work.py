from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import UserShort


class RepairMaterialBase(BaseModel):
    name: str
    quantity: float
    unit: Optional[str] = None
    cost: Optional[float] = None


class RepairMaterialCreate(RepairMaterialBase):
    pass


class RepairMaterialRead(RepairMaterialBase):
    id: int

    model_config = {"from_attributes": True}


class DiagnosticBase(BaseModel):
    request_id: int
    performed_at: datetime
    findings: str
    recommended_action: Optional[str] = None
    estimated_repair_hours: Optional[float] = None


class DiagnosticCreate(DiagnosticBase):
    pass


class DiagnosticRead(DiagnosticBase):
    id: int
    performed_by_id: int
    performed_by: Optional[UserShort] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RepairBase(BaseModel):
    request_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    work_description: str
    labor_hours: Optional[float] = None
    result: Optional[str] = None


class RepairCreate(RepairBase):
    materials: List[RepairMaterialCreate] = []


class RepairRead(RepairBase):
    id: int
    performed_by_id: int
    performed_by: Optional[UserShort] = None
    materials: List[RepairMaterialRead] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportBase(BaseModel):
    request_id: int
    report_type: str = "completion"
    summary: str
    recommendations: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportRead(ReportBase):
    id: int
    created_by_id: int
    created_by: Optional[UserShort] = None
    created_at: datetime

    model_config = {"from_attributes": True}

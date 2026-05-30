from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class PriorityCount(BaseModel):
    priority: str
    count: int


class EquipmentFaultCount(BaseModel):
    equipment_name: str
    equipment_id: int
    fault_count: int


class ServicePerformance(BaseModel):
    service_name: str
    service_id: int
    total_requests: int
    completed_requests: int
    avg_completion_hours: Optional[float] = None


class DashboardStats(BaseModel):
    total_open_requests: int
    critical_requests: int
    overdue_ppr_tasks: int
    equipment_broken: int
    requests_by_status: List[StatusCount]
    requests_by_priority: List[PriorityCount]
    recent_activity: List[Dict[str, Any]]


class AnalyticsReport(BaseModel):
    requests_by_status: List[StatusCount]
    requests_by_priority: List[PriorityCount]
    equipment_faults: List[EquipmentFaultCount]
    service_performance: List[ServicePerformance]
    ppr_completion_rate: float
    monthly_requests: List[Dict[str, Any]]

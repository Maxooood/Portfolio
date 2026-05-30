from app.schemas.user import UserRead, UserCreate, UserUpdate, UserShort, Token, LoginRequest
from app.schemas.equipment import EquipmentRead, EquipmentCreate, EquipmentUpdate, EquipmentNormRead, EquipmentNormCreate, EquipmentNormUpdate
from app.schemas.ppr import PprScheduleRead, PprTaskRead, PprTaskUpdate, GenerateScheduleRequest, PprScheduleWithTasks
from app.schemas.request import RequestRead, RequestCreate, RequestUpdate, RequestDetail, FaultTypeRead, FaultTypeCreate, StatusHistoryRead
from app.schemas.work import DiagnosticRead, DiagnosticCreate, RepairRead, RepairCreate, ReportRead, ReportCreate
from app.schemas.service import AuxiliaryServiceRead, AuxiliaryServiceCreate, AuxiliaryServiceUpdate, RoutingRuleRead, RoutingRuleCreate, RoutingRuleUpdate
from app.schemas.analytics import DashboardStats, AnalyticsReport

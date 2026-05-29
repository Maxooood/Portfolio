from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.request import Request, RequestStatus
from app.models.equipment import Equipment
from app.models.ppr import PprTask
from app.schemas.analytics import (
    DashboardStats, AnalyticsReport,
    StatusCount, PriorityCount, EquipmentFaultCount, ServicePerformance,
)


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    # Open requests
    open_statuses = [RequestStatus.NEW, RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS, RequestStatus.WAITING_PARTS]
    open_result = await db.execute(
        select(func.count(Request.id)).where(Request.status.in_(open_statuses))
    )
    total_open = open_result.scalar() or 0

    # Critical requests
    critical_result = await db.execute(
        select(func.count(Request.id)).where(
            Request.status.in_(open_statuses),
            Request.priority == "critical"
        )
    )
    critical = critical_result.scalar() or 0

    # Overdue PPR tasks
    now = datetime.now(timezone.utc)
    overdue_result = await db.execute(
        select(func.count(PprTask.id)).where(
            PprTask.status == "planned",
            PprTask.planned_date < now
        )
    )
    overdue_ppr = overdue_result.scalar() or 0

    # Broken equipment
    broken_result = await db.execute(
        select(func.count(Equipment.id)).where(Equipment.status == "broken")
    )
    broken_eq = broken_result.scalar() or 0

    # Requests by status
    status_rows = await db.execute(
        select(Request.status, func.count(Request.id)).group_by(Request.status)
    )
    requests_by_status = [
        StatusCount(status=row[0], count=row[1]) for row in status_rows
    ]

    # Requests by priority
    priority_rows = await db.execute(
        select(Request.priority, func.count(Request.id)).group_by(Request.priority)
    )
    requests_by_priority = [
        PriorityCount(priority=row[0], count=row[1]) for row in priority_rows
    ]

    # Recent activity: last 10 requests
    recent_result = await db.execute(
        select(Request).order_by(Request.created_at.desc()).limit(10)
    )
    recent_requests = recent_result.scalars().all()
    recent_activity = [
        {
            "id": r.id,
            "request_number": r.request_number,
            "title": r.title,
            "status": r.status,
            "priority": r.priority,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent_requests
    ]

    return DashboardStats(
        total_open_requests=total_open,
        critical_requests=critical,
        overdue_ppr_tasks=overdue_ppr,
        equipment_broken=broken_eq,
        requests_by_status=requests_by_status,
        requests_by_priority=requests_by_priority,
        recent_activity=recent_activity,
    )


async def get_analytics_report(db: AsyncSession) -> AnalyticsReport:
    # Requests by status
    status_rows = await db.execute(
        select(Request.status, func.count(Request.id)).group_by(Request.status)
    )
    requests_by_status = [StatusCount(status=r[0], count=r[1]) for r in status_rows]

    # Requests by priority
    priority_rows = await db.execute(
        select(Request.priority, func.count(Request.id)).group_by(Request.priority)
    )
    requests_by_priority = [PriorityCount(priority=r[0], count=r[1]) for r in priority_rows]

    # Equipment faults
    from sqlalchemy.orm import aliased
    eq_fault_rows = await db.execute(
        select(Equipment.id, Equipment.name, func.count(Request.id))
        .join(Request, Request.equipment_id == Equipment.id)
        .group_by(Equipment.id, Equipment.name)
        .order_by(func.count(Request.id).desc())
        .limit(10)
    )
    equipment_faults = [
        EquipmentFaultCount(equipment_id=r[0], equipment_name=r[1], fault_count=r[2])
        for r in eq_fault_rows
    ]

    # Service performance
    from app.models.service import AuxiliaryService
    svc_rows = await db.execute(
        select(
            AuxiliaryService.id,
            AuxiliaryService.name,
            func.count(Request.id),
            func.sum(
                func.case(
                    (Request.status.in_(["completed", "closed"]), 1),
                    else_=0
                )
            )
        )
        .join(Request, Request.service_id == AuxiliaryService.id, isouter=True)
        .group_by(AuxiliaryService.id, AuxiliaryService.name)
    )
    service_performance = [
        ServicePerformance(
            service_id=r[0],
            service_name=r[1],
            total_requests=r[2] or 0,
            completed_requests=r[3] or 0,
        )
        for r in svc_rows
    ]

    # PPR completion rate
    total_ppr = (await db.execute(select(func.count(PprTask.id)))).scalar() or 0
    completed_ppr = (await db.execute(
        select(func.count(PprTask.id)).where(PprTask.status == "completed")
    )).scalar() or 0
    ppr_rate = (completed_ppr / total_ppr * 100) if total_ppr > 0 else 0.0

    # Monthly requests (last 6 months)
    from datetime import date
    monthly = []
    today = date.today()
    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year - (i + 1 - today.month) // 12 if (today.month - i) <= 0 else today.year
        # Simpler calculation
        import calendar as cal
        d = today.replace(day=1)
        # Go back i months
        for _ in range(i):
            d = (d - timedelta(days=1)).replace(day=1)
        month_label = d.strftime("%Y-%m")
        count_result = await db.execute(
            select(func.count(Request.id)).where(
                Request.created_at >= datetime(d.year, d.month, 1, tzinfo=timezone.utc)
            )
        )
        monthly.append({"month": month_label, "count": count_result.scalar() or 0})

    return AnalyticsReport(
        requests_by_status=requests_by_status,
        requests_by_priority=requests_by_priority,
        equipment_faults=equipment_faults,
        service_performance=service_performance,
        ppr_completion_rate=round(ppr_rate, 1),
        monthly_requests=monthly,
    )

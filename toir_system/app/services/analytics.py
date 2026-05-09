import logging
from datetime import datetime, timezone
from sqlalchemy import func
from app.extensions import db
from app.models.request import Request, RequestStatus
from app.models.equipment import Equipment

logger = logging.getLogger(__name__)


def get_summary_stats(date_from: datetime = None, date_to: datetime = None) -> dict:
    query = Request.query
    if date_from:
        query = query.filter(Request.created_at >= date_from)
    if date_to:
        query = query.filter(Request.created_at <= date_to)

    total = query.count()
    by_status = dict(
        db.session.query(Request.status, func.count(Request.id))
        .filter(Request.created_at >= date_from if date_from else True)
        .filter(Request.created_at <= date_to if date_to else True)
        .group_by(Request.status)
        .all()
    )
    by_priority = dict(
        db.session.query(Request.priority, func.count(Request.id))
        .filter(Request.created_at >= date_from if date_from else True)
        .filter(Request.created_at <= date_to if date_to else True)
        .group_by(Request.priority)
        .all()
    )

    closed_requests = query.filter(
        Request.status == RequestStatus.CLOSED,
        Request.completed_at.isnot(None),
    ).all()

    avg_resolution_hours = None
    if closed_requests:
        total_hours = sum(
            (r.completed_at - r.created_at).total_seconds() / 3600
            for r in closed_requests
            if r.completed_at and r.created_at
        )
        avg_resolution_hours = round(total_hours / len(closed_requests), 2)

    logger.info(f'Summary stats computed: total={total}, avg_resolution={avg_resolution_hours}h')
    return {
        'total_requests': total,
        'by_status': by_status,
        'by_priority': by_priority,
        'avg_resolution_hours': avg_resolution_hours,
        'closed_count': len(closed_requests),
    }


def get_equipment_fault_stats() -> list[dict]:
    rows = (
        db.session.query(
            Equipment.id,
            Equipment.name,
            Equipment.inventory_number,
            func.count(Request.id).label('fault_count'),
        )
        .join(Request, Request.equipment_id == Equipment.id)
        .group_by(Equipment.id, Equipment.name, Equipment.inventory_number)
        .order_by(func.count(Request.id).desc())
        .all()
    )
    return [
        {
            'equipment_id': r.id,
            'equipment_name': r.name,
            'inventory_number': r.inventory_number,
            'fault_count': r.fault_count,
        }
        for r in rows
    ]


def get_service_performance() -> list[dict]:
    from app.models.service import AuxiliaryService
    rows = (
        db.session.query(
            AuxiliaryService.id,
            AuxiliaryService.name,
            func.count(Request.id).label('total'),
            func.sum(
                func.extract('epoch', Request.completed_at - Request.started_at) / 3600
            ).label('total_hours'),
        )
        .join(Request, Request.service_id == AuxiliaryService.id)
        .filter(Request.completed_at.isnot(None), Request.started_at.isnot(None))
        .group_by(AuxiliaryService.id, AuxiliaryService.name)
        .all()
    )
    result = []
    for r in rows:
        avg_hours = round(r.total_hours / r.total, 2) if r.total else None
        result.append({
            'service_id': r.id,
            'service_name': r.name,
            'total_requests': r.total,
            'avg_resolution_hours': avg_hours,
        })
    return result

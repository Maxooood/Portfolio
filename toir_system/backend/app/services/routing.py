from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.service import RoutingRule
from app.models.request import Request


async def auto_assign_executor(db: AsyncSession, request: Request) -> int | None:
    """Try to auto-assign executor based on routing rules."""
    q = select(RoutingRule).where(RoutingRule.is_active == True).order_by(RoutingRule.order)

    filters = []
    if request.service_id:
        filters.append(RoutingRule.service_id == request.service_id)

    if filters:
        q = q.where(*filters)

    result = await db.execute(q)
    rules = result.scalars().all()

    for rule in rules:
        # Check if rule matches
        if rule.equipment_type and request.equipment and request.equipment.equipment_type:
            if rule.equipment_type != request.equipment.equipment_type:
                continue
        if rule.fault_type_id and request.fault_type_id:
            if rule.fault_type_id != request.fault_type_id:
                continue
        if rule.priority and rule.priority != request.priority:
            continue
        if rule.executor_id:
            return rule.executor_id

    return None

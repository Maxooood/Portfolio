from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.user import UserShort

router = APIRouter(prefix="/admin", tags=["admin"])


class AuditLogRead:
    pass


from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict


class AuditLogResponse(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
    user: Optional[UserShort] = None

    model_config = {"from_attributes": True}


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(AuditLog)
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    from app.models.request import Request
    from app.models.equipment import Equipment

    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_equipment = (await db.execute(select(func.count(Equipment.id)))).scalar()
    total_requests = (await db.execute(select(func.count(Request.id)))).scalar()

    return {
        "total_users": total_users,
        "total_equipment": total_equipment,
        "total_requests": total_requests,
    }

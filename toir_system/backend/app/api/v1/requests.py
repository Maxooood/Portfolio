from datetime import datetime, timezone
from typing import List, Optional
import random
import string

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.request import Request, StatusHistory, FaultType, RequestStatus
from app.schemas.request import (
    RequestRead, RequestCreate, RequestUpdate, RequestDetail,
    FaultTypeRead, FaultTypeCreate, FaultTypeUpdate, StatusHistoryRead,
)

router = APIRouter(prefix="/requests", tags=["requests"])


def _request_opts():
    return [
        selectinload(Request.equipment),
        selectinload(Request.initiator),
        selectinload(Request.executor),
        selectinload(Request.fault_type),
    ]


def _request_detail_opts():
    return _request_opts() + [
        selectinload(Request.status_history).selectinload(StatusHistory.changed_by),
    ]


@router.get("", response_model=List[RequestRead])
async def list_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    service_id: Optional[int] = Query(None),
    equipment_id: Optional[int] = Query(None),
    executor_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Request).options(*_request_opts())
    if status_filter:
        q = q.where(Request.status == status_filter)
    if priority:
        q = q.where(Request.priority == priority)
    if service_id:
        q = q.where(Request.service_id == service_id)
    if equipment_id:
        q = q.where(Request.equipment_id == equipment_id)
    if executor_id:
        q = q.where(Request.executor_id == executor_id)
    # Executors only see their requests
    if current_user.role == UserRole.EXECUTOR:
        q = q.where(Request.executor_id == current_user.id)
    q = q.order_by(Request.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(
    data: RequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER, UserRole.SHIFT_MANAGER
    )),
):
    suffix = ''.join(random.choices(string.digits, k=6))
    req_number = f"REQ-{datetime.now().year}-{suffix}"

    request = Request(
        request_number=req_number,
        initiator_id=current_user.id,
        **data.model_dump(),
    )
    db.add(request)
    await db.flush()

    history = StatusHistory(
        request_id=request.id,
        old_status=None,
        new_status=RequestStatus.NEW,
        changed_by_id=current_user.id,
    )
    db.add(history)
    await db.commit()

    result = await db.execute(
        select(Request).where(Request.id == request.id).options(*_request_opts())
    )
    return result.scalar_one()


@router.get("/{req_id}", response_model=RequestDetail)
async def get_request(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Request).where(Request.id == req_id).options(*_request_detail_opts())
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


@router.patch("/{req_id}", response_model=RequestRead)
async def update_request(
    req_id: int,
    data: RequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Request).where(Request.id == req_id).options(*_request_opts())
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = req.status
    comment = data.comment
    update_data = data.model_dump(exclude_unset=True, exclude={"comment"})

    for field, value in update_data.items():
        setattr(req, field, value)

    new_status = req.status
    if new_status != old_status:
        if new_status == RequestStatus.CLOSED:
            req.closed_at = datetime.now(timezone.utc)
        history = StatusHistory(
            request_id=req.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=current_user.id,
            comment=comment,
        )
        db.add(history)

    await db.commit()
    await db.refresh(req)
    return req


# Fault types
ft_router = APIRouter(prefix="/fault-types", tags=["fault-types"])


@ft_router.get("", response_model=List[FaultTypeRead])
async def list_fault_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(FaultType).order_by(FaultType.name))
    return result.scalars().all()


@ft_router.post("", response_model=FaultTypeRead, status_code=status.HTTP_201_CREATED)
async def create_fault_type(
    data: FaultTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    ft = FaultType(**data.model_dump())
    db.add(ft)
    await db.commit()
    await db.refresh(ft)
    return ft


@ft_router.patch("/{ft_id}", response_model=FaultTypeRead)
async def update_fault_type(
    ft_id: int,
    data: FaultTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    result = await db.execute(select(FaultType).where(FaultType.id == ft_id))
    ft = result.scalar_one_or_none()
    if not ft:
        raise HTTPException(status_code=404, detail="FaultType not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ft, field, value)
    await db.commit()
    await db.refresh(ft)
    return ft

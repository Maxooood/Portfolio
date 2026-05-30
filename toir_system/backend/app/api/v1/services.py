from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.service import AuxiliaryService, RoutingRule
from app.schemas.service import (
    AuxiliaryServiceRead, AuxiliaryServiceCreate, AuxiliaryServiceUpdate,
    RoutingRuleRead, RoutingRuleCreate, RoutingRuleUpdate,
)

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=List[AuxiliaryServiceRead])
async def list_services(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AuxiliaryService).order_by(AuxiliaryService.name))
    return result.scalars().all()


@router.post("", response_model=AuxiliaryServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: AuxiliaryServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    svc = AuxiliaryService(**data.model_dump())
    db.add(svc)
    await db.commit()
    await db.refresh(svc)
    return svc


@router.patch("/{svc_id}", response_model=AuxiliaryServiceRead)
async def update_service(
    svc_id: int,
    data: AuxiliaryServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    result = await db.execute(select(AuxiliaryService).where(AuxiliaryService.id == svc_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(svc, field, value)
    await db.commit()
    await db.refresh(svc)
    return svc


@router.delete("/{svc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    svc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(AuxiliaryService).where(AuxiliaryService.id == svc_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(svc)
    await db.commit()


# Routing rules
rr_router = APIRouter(prefix="/routing-rules", tags=["routing-rules"])


@rr_router.get("", response_model=List[RoutingRuleRead])
async def list_routing_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RoutingRule).order_by(RoutingRule.order))
    return result.scalars().all()


@rr_router.post("", response_model=RoutingRuleRead, status_code=status.HTTP_201_CREATED)
async def create_routing_rule(
    data: RoutingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    rr = RoutingRule(**data.model_dump())
    db.add(rr)
    await db.commit()
    await db.refresh(rr)
    return rr


@rr_router.patch("/{rr_id}", response_model=RoutingRuleRead)
async def update_routing_rule(
    rr_id: int,
    data: RoutingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    result = await db.execute(select(RoutingRule).where(RoutingRule.id == rr_id))
    rr = result.scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rr, field, value)
    await db.commit()
    await db.refresh(rr)
    return rr


@rr_router.delete("/{rr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routing_rule(
    rr_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    result = await db.execute(select(RoutingRule).where(RoutingRule.id == rr_id))
    rr = result.scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    await db.delete(rr)
    await db.commit()

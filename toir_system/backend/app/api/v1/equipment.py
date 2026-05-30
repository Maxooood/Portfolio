from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.equipment import Equipment, EquipmentNorm
from app.schemas.equipment import (
    EquipmentRead, EquipmentCreate, EquipmentUpdate,
    EquipmentNormRead, EquipmentNormCreate, EquipmentNormUpdate,
)

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=List[EquipmentRead])
async def list_equipment(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Equipment)
    if status:
        q = q.where(Equipment.status == status)
    if department:
        q = q.where(Equipment.department == department)
    result = await db.execute(q.order_by(Equipment.name))
    return result.scalars().all()


@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    data: EquipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)),
):
    eq = Equipment(**data.model_dump())
    db.add(eq)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.get("/{eq_id}", response_model=EquipmentRead)
async def get_equipment(
    eq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Equipment).where(Equipment.id == eq_id))
    eq = result.scalar_one_or_none()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@router.patch("/{eq_id}", response_model=EquipmentRead)
async def update_equipment(
    eq_id: int,
    data: EquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)),
):
    result = await db.execute(select(Equipment).where(Equipment.id == eq_id))
    eq = result.scalar_one_or_none()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(eq, field, value)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.delete("/{eq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    eq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(Equipment).where(Equipment.id == eq_id))
    eq = result.scalar_one_or_none()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    await db.delete(eq)
    await db.commit()


# Norms endpoints
@router.get("/{eq_id}/norms", response_model=List[EquipmentNormRead])
async def list_norms(
    eq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EquipmentNorm).where(EquipmentNorm.equipment_id == eq_id)
    )
    return result.scalars().all()


@router.post("/{eq_id}/norms", response_model=EquipmentNormRead, status_code=status.HTTP_201_CREATED)
async def create_norm(
    eq_id: int,
    data: EquipmentNormCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PPR_ENGINEER)),
):
    norm = EquipmentNorm(**{**data.model_dump(), "equipment_id": eq_id})
    db.add(norm)
    await db.commit()
    await db.refresh(norm)
    return norm


@router.patch("/{eq_id}/norms/{norm_id}", response_model=EquipmentNormRead)
async def update_norm(
    eq_id: int,
    norm_id: int,
    data: EquipmentNormUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PPR_ENGINEER)),
):
    result = await db.execute(
        select(EquipmentNorm).where(EquipmentNorm.id == norm_id, EquipmentNorm.equipment_id == eq_id)
    )
    norm = result.scalar_one_or_none()
    if not norm:
        raise HTTPException(status_code=404, detail="Norm not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(norm, field, value)
    await db.commit()
    await db.refresh(norm)
    return norm

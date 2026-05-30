from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.work import Diagnostic, Repair, RepairMaterial
from app.models.report import Report
from app.schemas.work import (
    DiagnosticRead, DiagnosticCreate,
    RepairRead, RepairCreate,
    ReportRead, ReportCreate,
)

router = APIRouter(tags=["work"])


@router.get("/requests/{req_id}/diagnostics", response_model=List[DiagnosticRead])
async def list_diagnostics(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Diagnostic).where(Diagnostic.request_id == req_id)
        .options(selectinload(Diagnostic.performed_by))
        .order_by(Diagnostic.performed_at)
    )
    return result.scalars().all()


@router.post("/requests/{req_id}/diagnostics", response_model=DiagnosticRead, status_code=status.HTTP_201_CREATED)
async def create_diagnostic(
    req_id: int,
    data: DiagnosticCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EXECUTOR, UserRole.DISPATCHER)),
):
    diag = Diagnostic(
        **{**data.model_dump(), "request_id": req_id, "performed_by_id": current_user.id}
    )
    db.add(diag)
    await db.commit()
    await db.refresh(diag)
    return diag


@router.get("/requests/{req_id}/repairs", response_model=List[RepairRead])
async def list_repairs(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Repair).where(Repair.request_id == req_id)
        .options(selectinload(Repair.performed_by), selectinload(Repair.materials))
        .order_by(Repair.started_at)
    )
    return result.scalars().all()


@router.post("/requests/{req_id}/repairs", response_model=RepairRead, status_code=status.HTTP_201_CREATED)
async def create_repair(
    req_id: int,
    data: RepairCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EXECUTOR, UserRole.DISPATCHER)),
):
    materials = data.materials
    repair_data = data.model_dump(exclude={"materials"})
    repair = Repair(
        **{**repair_data, "request_id": req_id, "performed_by_id": current_user.id}
    )
    db.add(repair)
    await db.flush()
    for m in materials:
        mat = RepairMaterial(**{**m.model_dump(), "repair_id": repair.id})
        db.add(mat)
    await db.commit()

    result = await db.execute(
        select(Repair).where(Repair.id == repair.id)
        .options(selectinload(Repair.performed_by), selectinload(Repair.materials))
    )
    return result.scalar_one()


@router.get("/requests/{req_id}/reports", response_model=List[ReportRead])
async def list_reports(
    req_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Report).where(Report.request_id == req_id)
        .options(selectinload(Report.created_by))
    )
    return result.scalars().all()


@router.post("/requests/{req_id}/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    req_id: int,
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EXECUTOR, UserRole.DISPATCHER, UserRole.MANAGER)),
):
    report = Report(
        **{**data.model_dump(), "request_id": req_id, "created_by_id": current_user.id}
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

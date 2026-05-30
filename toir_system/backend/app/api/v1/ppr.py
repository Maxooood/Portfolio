from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.ppr import PprSchedule, PprTask
from app.models.request import Request
from app.schemas.ppr import (
    PprScheduleRead, PprTaskRead, PprTaskUpdate,
    GenerateScheduleRequest, PprScheduleWithTasks,
)
from app.services.ppr_planner import generate_ppr_schedule

router = APIRouter(prefix="/ppr", tags=["ppr"])


@router.get("/schedules", response_model=List[PprScheduleRead])
async def list_schedules(
    year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(PprSchedule).options(
        selectinload(PprSchedule.generated_by),
        selectinload(PprSchedule.approved_by),
    )
    if year:
        q = q.where(PprSchedule.year == year)
    result = await db.execute(q.order_by(PprSchedule.year.desc(), PprSchedule.month.desc()))
    return result.scalars().all()


@router.post("/schedules/generate", response_model=PprScheduleRead, status_code=status.HTTP_201_CREATED)
async def generate_schedule(
    data: GenerateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.PPR_ENGINEER)),
):
    # Check if schedule for this month/year already exists
    existing = await db.execute(
        select(PprSchedule).where(PprSchedule.year == data.year, PprSchedule.month == data.month)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Schedule for this month already exists")

    schedule = await generate_ppr_schedule(db, data.year, data.month, current_user.id)
    await db.refresh(schedule)
    return schedule


@router.get("/schedules/{schedule_id}", response_model=PprScheduleWithTasks)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PprSchedule)
        .where(PprSchedule.id == schedule_id)
        .options(
            selectinload(PprSchedule.generated_by),
            selectinload(PprSchedule.approved_by),
            selectinload(PprSchedule.tasks).selectinload(PprTask.equipment),
            selectinload(PprSchedule.tasks).selectinload(PprTask.norm),
        )
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.get("/schedules/{schedule_id}/tasks", response_model=List[PprTaskRead])
async def get_schedule_tasks(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PprTask)
        .where(PprTask.schedule_id == schedule_id)
        .options(selectinload(PprTask.equipment), selectinload(PprTask.norm))
        .order_by(PprTask.planned_date)
    )
    return result.scalars().all()


@router.post("/schedules/{schedule_id}/approve", response_model=PprScheduleRead)
async def approve_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER)),
):
    from datetime import datetime, timezone
    result = await db.execute(select(PprSchedule).where(PprSchedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule.is_approved = True
    schedule.approved_by_id = current_user.id
    schedule.approved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.put("/tasks/{task_id}/status", response_model=PprTaskRead)
async def update_task_status(
    task_id: int,
    data: PprTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PprTask).where(PprTask.id == task_id)
        .options(selectinload(PprTask.equipment), selectinload(PprTask.norm))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/create-request", response_model=dict)
async def create_request_from_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.DISPATCHER, UserRole.PPR_ENGINEER)),
):
    from datetime import datetime, timezone
    from app.models.request import Request, StatusHistory, RequestStatus, RequestType
    import random
    import string

    result = await db.execute(
        select(PprTask).where(PprTask.id == task_id).options(selectinload(PprTask.norm))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.request_id:
        raise HTTPException(status_code=400, detail="Request already created for this task")

    # Generate request number
    suffix = ''.join(random.choices(string.digits, k=6))
    req_number = f"PPR-{datetime.now().year}-{suffix}"

    norm_desc = task.norm.description if task.norm else "Плановое техническое обслуживание"
    request = Request(
        request_number=req_number,
        request_type=RequestType.PPR,
        title=f"ТО: {norm_desc}",
        description=f"Создано из плана ППР (задача #{task_id})",
        status=RequestStatus.NEW,
        priority="medium",
        equipment_id=task.equipment_id,
        initiator_id=current_user.id,
        planned_start=task.planned_date,
    )
    db.add(request)
    await db.flush()

    # Add status history
    history = StatusHistory(
        request_id=request.id,
        old_status=None,
        new_status=RequestStatus.NEW,
        changed_by_id=current_user.id,
        comment="Создано из плана ППР",
    )
    db.add(history)

    task.request_id = request.id
    task.status = "in_progress"
    await db.commit()

    return {"request_id": request.id, "request_number": req_number}

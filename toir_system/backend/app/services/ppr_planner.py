import calendar
from datetime import datetime, timezone, date, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.equipment import Equipment, EquipmentNorm
from app.models.ppr import PprSchedule, PprTask


async def generate_ppr_schedule(
    db: AsyncSession, year: int, month: int, generated_by_id: int
) -> PprSchedule:
    """Generate PPR schedule for a given year/month based on equipment norms."""
    # Get all active equipment
    eq_result = await db.execute(
        select(Equipment).where(Equipment.status != "decommissioned")
    )
    equipments = eq_result.scalars().all()

    # Get all active norms
    norm_result = await db.execute(
        select(EquipmentNorm).where(EquipmentNorm.is_active == True)
    )
    norms = norm_result.scalars().all()

    # Build norm map: equipment_id -> [norms]
    norm_map: dict[int, List[EquipmentNorm]] = {}
    for norm in norms:
        norm_map.setdefault(norm.equipment_id, []).append(norm)

    # Create schedule record
    schedule = PprSchedule(
        year=year,
        month=month,
        generated_by_id=generated_by_id,
        is_approved=False,
    )
    db.add(schedule)
    await db.flush()

    # Calculate days in month
    _, days_in_month = calendar.monthrange(year, month)
    month_start = date(year, month, 1)
    month_end = date(year, month, days_in_month)

    tasks_created = 0
    for eq in equipments:
        eq_norms = norm_map.get(eq.id, [])
        for norm in eq_norms:
            # Calculate planned dates within the month based on interval
            # Start from first day of month and iterate by interval
            current_date = month_start
            while current_date <= month_end:
                planned_dt = datetime(
                    current_date.year, current_date.month, current_date.day,
                    9, 0, 0, tzinfo=timezone.utc
                )
                task = PprTask(
                    schedule_id=schedule.id,
                    equipment_id=eq.id,
                    norm_id=norm.id,
                    planned_date=planned_dt,
                    status="planned",
                )
                db.add(task)
                tasks_created += 1

                # Next occurrence
                if norm.interval_days >= days_in_month:
                    # Only one task this month
                    break
                current_date = current_date + timedelta(days=norm.interval_days)

    await db.commit()
    return schedule

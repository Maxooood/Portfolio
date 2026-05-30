"""Celery tasks for PPR auto-scheduling."""
import os
from datetime import datetime, timezone

try:
    from celery import Celery
    from celery.schedules import crontab

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    celery_app = Celery(
        "toir_worker",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["app.worker.tasks"],
    )

    celery_app.conf.beat_schedule = {
        "mark-overdue-ppr-tasks": {
            "task": "app.worker.tasks.mark_overdue_ppr_tasks",
            "schedule": crontab(hour=0, minute=5),  # daily at 00:05
        },
    }

    @celery_app.task(name="app.worker.tasks.mark_overdue_ppr_tasks")
    def mark_overdue_ppr_tasks():
        """Mark planned PPR tasks that are past their date as overdue."""
        import asyncio
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import select, update
        from app.models.ppr import PprTask

        async def _run():
            async with AsyncSessionLocal() as db:
                now = datetime.now(timezone.utc)
                await db.execute(
                    update(PprTask)
                    .where(PprTask.status == "planned", PprTask.planned_date < now)
                    .values(status="overdue")
                )
                await db.commit()

        asyncio.run(_run())
        return "Done"

except ImportError:
    # Celery not available
    pass

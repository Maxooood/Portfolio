from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.analytics import DashboardStats, AnalyticsReport
from app.services.analytics import get_dashboard_stats, get_analytics_report

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_dashboard_stats(db)


@router.get("/report", response_model=AnalyticsReport)
async def analytics_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_analytics_report(db)

from fastapi import APIRouter

from app.api.v1 import auth, users, equipment, ppr, requests, work, services, analytics, admin

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(equipment.router)
api_router.include_router(ppr.router)
api_router.include_router(requests.router)
api_router.include_router(requests.ft_router)
api_router.include_router(work.router)
api_router.include_router(services.router)
api_router.include_router(services.rr_router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)

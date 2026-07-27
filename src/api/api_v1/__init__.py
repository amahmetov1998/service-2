from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .phone_details import router as phones_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(phones_router)

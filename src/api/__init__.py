from fastapi import APIRouter
from .booking import router as bookings_routers
from .user import router as user_routers
from .schedule import router as schedule_routers


router = APIRouter()


router.include_router(
    bookings_routers,
)

router.include_router(
    user_routers,
)

router.include_router(
    schedule_routers,
)
from fastapi import APIRouter
from .booking import router as bookings_routers
from .user import router as user_routers


router = APIRouter()


router.include_router(
    bookings_routers,
)

router.include_router(
    user_routers,
)
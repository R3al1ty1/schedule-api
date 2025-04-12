from fastapi import APIRouter
from .booking import router as router_api_v1


router = APIRouter()


router.include_router(
    router_api_v1,
    prefix="/v1",
)
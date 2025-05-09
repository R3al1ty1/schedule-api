from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from core.utils import verify_admin


router = APIRouter(tags=["Users"])

db = db_helper.session_getter

@router.get("/users/check-admin", response_model=dict)
async def check_is_admin(
    user_id: int = Header(...),
    db: AsyncSession = Depends(db)
):
    """
    Проверяет, является ли пользователь администратором.
    """
    is_admin = await verify_admin(user_id, db)
    return {"is_admin": is_admin}

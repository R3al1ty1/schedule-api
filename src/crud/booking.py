from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import booking as booking_model
from core.schemas import booking as booking_schema


async def get_bookings_db(
    db: AsyncSession,
    is_admin: bool = False,
    user_id: Optional[int] = None
) -> List[booking_schema.Booking]:
    stmt = select(booking_model.Booking).options(selectinload(booking_model.Booking.comments))
    
    if not is_admin and user_id:
        stmt = stmt.where(booking_model.Booking.user_id == user_id)
    elif not is_admin and not user_id:
        return []

    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    return [booking_schema.Booking.model_validate(b) for b in bookings]
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import booking as booking_model


async def get_bookings_db(
    db: AsyncSession,
    is_admin: bool = False,
    user_id: int = None
) -> List[booking_model.Booking]:
    if is_admin and not user_id:
        stmt = select(booking_model.Booking)
        result = await db.execute(stmt)
        bookings = result.scalars().all()
        return bookings
    
    if user_id:
        stmt = select(booking_model.Booking).where(booking_model.Booking.user_id == user_id)
        result = await db.execute(stmt)
        bookings = result.scalars().all()
        return bookings
    
    return []
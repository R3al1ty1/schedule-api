from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import booking as booking_model
from core.schemas import booking as booking_schema


async def get_bookings_db(
    db: AsyncSession,
    is_admin: bool = False,
    user_id: Optional[int] = None
) -> List[booking_schema.Booking]:
    if is_admin and not user_id:
        stmt = select(booking_model.Booking)
    elif user_id:
        stmt = select(booking_model.Booking).where(booking_model.Booking.user_id == user_id)
    else:
        return []

    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    return [booking_schema.Booking.model_validate(booking) for booking in bookings]

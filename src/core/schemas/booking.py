from pydantic import BaseModel
from typing import Optional
from datetime import date


class BookingBase(BaseModel):
    id: int
    start_date: date
    end_date: date
    people_count: int
    event_theme: str
    event_description: Optional[str] = None


class BookingCreate(BookingBase):
    user_id: int


class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    people_count: Optional[int] = None
    event_theme: Optional[str] = None
    event_description: Optional[str] = None


class Booking(BookingBase):
    user_id: int
    status: str
    
    class Config:
        from_attributes = True


class BookingListRequest(BaseModel):
    admin_id: Optional[int] = None

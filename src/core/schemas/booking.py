from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from core.schemas.comment import Comment
from enum import Enum

class SortField(str, Enum):
    id = "id"
    start_date = "start_date"
    end_date = "end_date"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class BookingCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    people_count: int
    people_count_overall: int
    theme: str                    # было event_theme
    description: Optional[str] = None  # было event_description
    target_audience: Optional[str] = None
    name: Optional[str] = None
    registration: Optional[str] = None
    logistics: Optional[str] = None
    type: Optional[str] = None
    place: Optional[str] = None
    participants_accomodation: Optional[str] = None
    experts_count: Optional[int] = None
    curator_fio: Optional[str] = None
    curator_position: Optional[str] = None
    curator_contact: Optional[str] = None
    other_info: Optional[str] = None

    class Config:
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }

class BookingUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    people_count: Optional[int] = None
    people_count_overall: Optional[int] = None
    theme: Optional[str] = None           # было event_theme
    description: Optional[str] = None     # было event_description
    target_audience: Optional[str] = None
    name: Optional[str] = None
    registration: Optional[str] = None
    logistics: Optional[str] = None
    type: Optional[str] = None
    place: Optional[str] = None
    participants_accomodation: Optional[str] = None
    experts_count: Optional[int] = None
    curator_fio: Optional[str] = None
    curator_position: Optional[str] = None
    curator_contact: Optional[str] = None
    other_info: Optional[str] = None

class Booking(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: date
    people_count: int
    people_count_overall: Optional[int] = None
    theme: str                    # было event_theme
    description: Optional[str] = None  # было event_description
    status: str
    target_audience: Optional[str] = None
    name: Optional[str] = None
    registration: Optional[str] = None
    logistics: Optional[str] = None
    type: Optional[str] = None
    place: Optional[str] = None
    participants_accomodation: Optional[str] = None
    experts_count: Optional[int] = None
    curator_fio: Optional[str] = None
    curator_position: Optional[str] = None
    curator_contact: Optional[str] = None
    other_info: Optional[str] = None
    comments: List[Comment] = []
    
    model_config = {
        "from_attributes": True
    }

class BookingListRequest(BaseModel):
    admin_id: Optional[int] = None


class BookingListResponse(BaseModel):
    result: List[Booking]


class CalendarDay(BaseModel):
    date: str
    total_people: int
    names: List[str]

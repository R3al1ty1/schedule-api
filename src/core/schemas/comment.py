from pydantic import BaseModel

class CommentBase(BaseModel):
    comment: str
    booking_id: int


class Comment(CommentBase):
    id: int
    
    class Config:
        from_attributes = True
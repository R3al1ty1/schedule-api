from pydantic import BaseModel


class Admin(BaseModel):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

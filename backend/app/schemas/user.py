from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    avatar: str | None = None

class UserProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    avatar: str | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

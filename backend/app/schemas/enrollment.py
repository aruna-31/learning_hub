from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class EnrollmentCreate(BaseModel):
    course_id: UUID = Field(..., description="UUID of the course to enroll in")

class EnrollmentResponse(BaseModel):
    id: UUID
    user_id: int
    course_id: UUID
    enrolled_at: datetime
    progress_percent: float
    completed_at: datetime | None

    class Config:
        from_attributes = True

class EnrollmentListResponse(BaseModel):
    items: list[EnrollmentResponse]
    total: int
    page: int
    size: int
    pages: int

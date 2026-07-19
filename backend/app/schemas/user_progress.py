from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ProgressToggle(BaseModel):
    enrollment_id: UUID = Field(..., description="UUID of the course enrollment")
    step_id: UUID = Field(..., description="UUID of the roadmap step")
    completed: bool = Field(True, description="True to mark completed, False to mark incomplete")

class ProgressResponse(BaseModel):
    id: UUID
    enrollment_id: UUID
    step_id: UUID
    completed_at: datetime

    class Config:
        from_attributes = True

class EnrollmentProgressStatus(BaseModel):
    enrollment_id: UUID
    course_id: UUID
    course_title: str
    completed_steps_count: int
    total_steps_count: int
    progress_percent: float
    is_completed: bool
    completed_at: datetime | None
    completed_step_ids: list[UUID]

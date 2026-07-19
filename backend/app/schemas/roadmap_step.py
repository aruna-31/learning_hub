from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class RoadmapStepBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="Title of the roadmap step")
    description: str | None = Field(None, description="Detailed instructions or description of the step")
    step_order: int = Field(..., ge=1, description="Sequential position of the step (starts at 1)")
    course_id: UUID = Field(..., description="UUID of the course this step belongs to")

class RoadmapStepCreate(RoadmapStepBase):
    pass

class RoadmapStepUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None)
    step_order: int | None = Field(None, ge=1)
    course_id: UUID | None = Field(None)

class RoadmapStepResponse(RoadmapStepBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoadmapStepListResponse(BaseModel):
    items: list[RoadmapStepResponse]
    total: int
    page: int
    size: int
    pages: int

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ActiveCourseProgress(BaseModel):
    enrollment_id: UUID
    course_id: UUID
    course_title: str
    progress_percent: float
    enrolled_at: datetime
    completed_at: datetime | None

class DashboardMetricsResponse(BaseModel):
    total_enrolled: int = Field(0, description="Total number of courses enrolled")
    in_progress_count: int = Field(0, description="Count of courses currently in progress")
    completed_count: int = Field(0, description="Count of courses completed")
    total_bookmarks: int = Field(0, description="Total number of bookmarked resources")
    total_notes: int = Field(0, description="Total number of steps with personal notes")
    recent_courses: list[ActiveCourseProgress] = Field([], description="List of recently enrolled courses with their progress")

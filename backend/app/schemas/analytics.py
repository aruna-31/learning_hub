from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class CategoryProgressDistribution(BaseModel):
    category_name: str
    enrolled_courses_count: int
    average_progress_percent: float

class AnalyticsCourseDetail(BaseModel):
    course_id: UUID
    course_title: str
    total_steps_count: int
    completed_steps_count: int
    progress_percent: float
    duration_hours: int
    is_completed: bool

class AnalyticsResponse(BaseModel):
    total_study_hours_committed: int = Field(0, description="Sum of duration_hours of enrolled courses")
    overall_average_progress: float = Field(0.0, description="Average progress percent of all enrollments")
    category_distribution: list[CategoryProgressDistribution] = Field([], description="Enrollment counts and progress split by category")
    course_details: list[AnalyticsCourseDetail] = Field([], description="Detail breakdown of progress per course")

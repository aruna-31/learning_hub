from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID

class CourseBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="The title of the course")
    description: str = Field(..., min_length=10, description="The detailed description of the course")
    instructor_name: str = Field(..., min_length=2, max_length=100, description="Instructor's name")
    difficulty_level: str = Field("Beginner", description="Difficulty level: Beginner, Intermediate, Advanced")
    duration_hours: int = Field(0, ge=0, description="Estimated duration in hours")
    category_id: UUID = Field(..., description="UUID of the category this course belongs to")

class CourseCreate(CourseBase):
    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        allowed = ["Beginner", "Intermediate", "Advanced"]
        val = value.strip().capitalize()
        if val not in allowed:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed)}")
        return val

class CourseUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, min_length=10)
    instructor_name: str | None = Field(None, min_length=2, max_length=100)
    difficulty_level: str | None = Field(None)
    duration_hours: int | None = Field(None, ge=0)
    category_id: UUID | None = Field(None)

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, value: str | None) -> str | None:
        if value is not None:
            allowed = ["Beginner", "Intermediate", "Advanced"]
            val = value.strip().capitalize()
            if val not in allowed:
                raise ValueError(f"Difficulty level must be one of: {', '.join(allowed)}")
            return val
        return value

class CourseResponse(CourseBase):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    total: int
    page: int
    size: int
    pages: int

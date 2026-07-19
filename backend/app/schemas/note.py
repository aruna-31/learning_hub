from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class NoteCreate(BaseModel):
    step_id: UUID = Field(..., description="UUID of the roadmap step to attach notes to")
    content: str = Field(..., min_length=1, description="Markdown text content of the note")

class NoteUpdate(BaseModel):
    content: str = Field(..., min_length=1, description="Markdown text content of the note")

class NoteResponse(BaseModel):
    id: UUID
    user_id: int
    step_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
    page: int
    size: int
    pages: int

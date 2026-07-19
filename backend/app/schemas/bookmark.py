from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.schemas.resource import ResourceResponse

class BookmarkCreate(BaseModel):
    resource_id: UUID = Field(..., description="UUID of the resource to bookmark")

class ExternalBookmarkCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    url: str = Field(..., description="External resource URL")
    type: str = Field("Other", description="Type: Video, Article, Document, Repository, Book, Dataset, Other")

class BookmarkResponse(BaseModel):
    id: UUID
    user_id: int
    resource_id: UUID
    created_at: datetime
    resource: ResourceResponse | None = None

    class Config:
        from_attributes = True

class BookmarkListResponse(BaseModel):
    items: list[BookmarkResponse]
    total: int
    page: int
    size: int
    pages: int

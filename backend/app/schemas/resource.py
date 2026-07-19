from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from uuid import UUID

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="Title of the resource")
    url: str = Field(..., description="Link to the resource")
    type: str = Field("Other", description="Type: Video, Article, Document, Repository, Book, Dataset, Other")
    step_id: UUID = Field(..., description="UUID of the roadmap step this resource belongs to")

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        val = value.strip()
        if not (val.startswith("http://") or val.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return val

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        allowed = ["Video", "Article", "Document", "Repository", "Book", "Dataset", "Other"]
        val = value.strip().capitalize()
        if val not in allowed:
            raise ValueError(f"Resource type must be one of: {', '.join(allowed)}")
        return val

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=200)
    url: str | None = Field(None)
    type: str | None = Field(None)
    step_id: UUID | None = Field(None)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is not None:
            val = value.strip()
            if not (val.startswith("http://") or val.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")
            return val
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str | None) -> str | None:
        if value is not None:
            allowed = ["Video", "Article", "Document", "Repository", "Book", "Dataset", "Other"]
            val = value.strip().capitalize()
            if val not in allowed:
                raise ValueError(f"Resource type must be one of: {', '.join(allowed)}")
            return val
        return value

class ResourceResponse(ResourceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResourceListResponse(BaseModel):
    items: list[ResourceResponse]
    total: int
    page: int
    size: int
    pages: int


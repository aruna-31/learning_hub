from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
import re

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="The name of the category")
    description: str | None = Field(None, max_length=500, description="The description of the category")

class CategoryCreate(CategoryBase):
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # Custom validation: ensure category name is not purely numeric or special characters
        if not re.search(r"[a-zA-Z]", value):
            raise ValueError("Category name must contain at least one letter.")
        return value.strip()

class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None:
            if not re.search(r"[a-zA-Z]", value):
                raise ValueError("Category name must contain at least one letter.")
            return value.strip()
        return value

class CategoryResponse(CategoryBase):
    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int

from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class CourseSchema(BaseModel):
    id: Optional[int] = None
    title: str
    url: str
    description: Optional[str] = None
    source: str

    model_config = {
        "from_attributes": True
    }

class RepositorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    full_name: str
    url: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class VideoSchema(BaseModel):
    id: Optional[int] = None
    title: str
    video_id: str
    url: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    channel_title: Optional[str] = None
    published_at: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class BookSchema(BaseModel):
    id: Optional[int] = None
    title: str
    authors: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    info_link: str
    publisher: Optional[str] = None
    published_date: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class DatasetSchema(BaseModel):
    id: Optional[int] = None
    title: str
    url: str
    description: Optional[str] = None
    size: Optional[str] = None
    creator: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class SearchResultSchema(BaseModel):
    course: Optional[CourseSchema] = None
    roadmap: List[Any] = []
    repositories: List[RepositorySchema] = []
    videos: List[VideoSchema] = []
    books: List[BookSchema] = []
    datasets: List[DatasetSchema] = []
    documentation: List[Dict[str, Any]] = []
    last_updated: str

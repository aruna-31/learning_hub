from app.database import Base
from app.models.user import User
from app.models.category import Category
from app.models.course import Course
from app.models.roadmap_step import RoadmapStep
from app.models.resource import Resource
from app.models.enrollment import Enrollment
from app.models.user_progress import UserProgress
from app.models.bookmark import Bookmark
from app.models.note import Note
from app.models.api_cache_metadata import APICacheMetadata
from app.models.search_history import SearchHistory
from app.models.cache_items import CourseCache, RepositoryCache, VideoCache, BookCache, DatasetCache
from app.models.roadmap import Roadmap

# Export all models for Alembic autodiscover or metadata creation
__all__ = [
    "Base", "User", "Category", "Course", "RoadmapStep", "Resource", "Enrollment", 
    "UserProgress", "Bookmark", "Note", "APICacheMetadata", "SearchHistory",
    "CourseCache", "RepositoryCache", "VideoCache", "BookCache", "DatasetCache", "Roadmap"
]



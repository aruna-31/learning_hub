from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from app.database import Base

class CourseCache(Base):
    """
    SQLAlchemy model representing the 'courses_cache' table.
    Stores cached courses/questions/answers normalized from Stack Exchange/other platforms.
    """
    __tablename__ = "courses_cache"

    id = Column(Integer, primary_key=True, index=True)
    api_cache_metadata_id = Column(Integer, ForeignKey("api_cache_metadata.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)

class RepositoryCache(Base):
    """
    SQLAlchemy model representing the 'repositories_cache' table.
    Stores cached repositories normalized from GitHub API.
    """
    __tablename__ = "repositories_cache"

    id = Column(Integer, primary_key=True, index=True)
    api_cache_metadata_id = Column(Integer, ForeignKey("api_cache_metadata.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    stars = Column(Integer, default=0, nullable=False)
    forks = Column(Integer, default=0, nullable=False)
    language = Column(String(100), nullable=True)

class VideoCache(Base):
    """
    SQLAlchemy model representing the 'videos_cache' table.
    Stores cached videos/playlists normalized from YouTube API.
    """
    __tablename__ = "videos_cache"

    id = Column(Integer, primary_key=True, index=True)
    api_cache_metadata_id = Column(Integer, ForeignKey("api_cache_metadata.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    video_id = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(Text, nullable=True)
    channel_title = Column(String(255), nullable=True)
    published_at = Column(String(100), nullable=True)

class BookCache(Base):
    """
    SQLAlchemy model representing the 'books_cache' table.
    Stores cached books normalized from Google Books API.
    """
    __tablename__ = "books_cache"

    id = Column(Integer, primary_key=True, index=True)
    api_cache_metadata_id = Column(Integer, ForeignKey("api_cache_metadata.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    authors = Column(Text, nullable=True)  # Comma separated authors
    description = Column(Text, nullable=True)
    thumbnail = Column(Text, nullable=True)
    info_link = Column(Text, nullable=False)
    publisher = Column(String(255), nullable=True)
    published_date = Column(String(100), nullable=True)

class DatasetCache(Base):
    """
    SQLAlchemy model representing the 'datasets_cache' table.
    Stores cached datasets normalized from Kaggle Dataset API or others.
    """
    __tablename__ = "datasets_cache"

    id = Column(Integer, primary_key=True, index=True)
    api_cache_metadata_id = Column(Integer, ForeignKey("api_cache_metadata.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    size = Column(String(100), nullable=True)
    creator = Column(String(255), nullable=True)

from sqlalchemy import Column, String, DateTime, func, Integer
from app.database import Base

class APICacheMetadata(Base):
    """
    SQLAlchemy model representing the 'api_cache_metadata' table.
    Tracks when a specific query's cache was last refreshed.
    """
    __tablename__ = "api_cache_metadata"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), unique=True, index=True, nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

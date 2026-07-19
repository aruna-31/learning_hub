from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database import Base

class SearchHistory(Base):
    """
    SQLAlchemy model representing the 'search_history' table.
    Tracks user searches.
    """
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    searched_at = Column(DateTime, default=func.now(), nullable=False)

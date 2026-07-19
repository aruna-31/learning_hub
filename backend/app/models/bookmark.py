import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Bookmark(Base):
    """
    SQLAlchemy model representing the 'bookmarks' table.
    Links users to resources for quick reference bookmarks.
    """
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource_bookmark"),
    )

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    resource = relationship("Resource")

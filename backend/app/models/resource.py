import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Resource(Base):
    """
    SQLAlchemy model representing the 'resources' table.
    Resources represent attachments/curated content for roadmap steps.
    """
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    type = Column(String(30), nullable=False, default="Other") # Video, Article, Document, Repository, Other
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    roadmap_step = relationship("RoadmapStep", back_populates="resources")

import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class RoadmapStep(Base):
    """
    SQLAlchemy model representing the 'roadmap_steps' table.
    Enforces a strict order of steps for a course.
    """
    __tablename__ = "roadmap_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    step_order = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("course_id", "step_order", name="uq_course_step_order"),
    )

    # Relationships
    course = relationship("Course", back_populates="roadmap_steps")
    resources = relationship("Resource", back_populates="roadmap_step", cascade="all, delete-orphan")

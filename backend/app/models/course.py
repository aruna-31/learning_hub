import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Course(Base):
    """
    SQLAlchemy model representing the 'courses' table.
    Uses UUID for primary keys to prevent ID enumeration.
    """
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), unique=True, index=True, nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    instructor_name = Column(String(100), nullable=False)
    difficulty_level = Column(String(20), nullable=False, default="Beginner") # Beginner, Intermediate, Advanced
    duration_hours = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="courses")
    roadmap_steps = relationship("RoadmapStep", back_populates="course", cascade="all, delete-orphan", order_by="RoadmapStep.step_order")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

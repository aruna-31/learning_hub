import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class UserProgress(Base):
    """
    SQLAlchemy model representing the 'user_progress' table.
    Tracks which steps of a course have been completed by a student.
    """
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    completed_at = Column(DateTime, default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("enrollment_id", "step_id", name="uq_enrollment_step_progress"),
    )

    # Relationships
    enrollment = relationship("Enrollment", back_populates="progress_records")
    roadmap_step = relationship("RoadmapStep")

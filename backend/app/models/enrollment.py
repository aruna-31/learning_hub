import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Enrollment(Base):
    """
    SQLAlchemy model representing the 'enrollments' table.
    Links users to courses to track their enrollment state.
    """
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    enrolled_at = Column(DateTime, default=func.now(), nullable=False)
    progress_percent = Column(Float, nullable=False, default=0.0)
    completed_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    progress_records = relationship("UserProgress", back_populates="enrollment", cascade="all, delete-orphan")

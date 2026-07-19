from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.repositories.base import BaseRepository
from app.models.enrollment import Enrollment
from uuid import UUID

class EnrollmentRepository(BaseRepository[Enrollment]):
    """
    Repository class specifically for Enrollment entities.
    """
    def __init__(self):
        super().__init__(Enrollment)

    def get_by_user_and_course(self, db: Session, user_id: int, course_id: UUID) -> Enrollment | None:
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.course_id == course_id
        ).first()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        user_id: int | None = None,
        course_id: UUID | None = None,
        sort_by: str = "enrolled_at",
        sort_order: str = "desc"
    ) -> tuple[list[Enrollment], int]:
        """
        Retrieves a list of enrollments with filtering, sorting, and pagination.
        """
        query = db.query(self.model)

        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        if course_id:
            query = query.filter(self.model.course_id == course_id)

        total_count = query.count()

        sort_field = getattr(self.model, sort_by, self.model.enrolled_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        items = query.offset(skip).limit(limit).all()

        return items, total_count

# Instantiated single instance for convenience
enrollment_repo = EnrollmentRepository()

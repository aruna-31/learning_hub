from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.enrollment import enrollment_repo
from app.repositories.course import course_repo
from app.schemas.enrollment import EnrollmentCreate
from app.models.enrollment import Enrollment
import uuid

class EnrollmentService:
    """
    Service class encapsulating business logic for Course Enrollment.
    """

    def enroll_user(self, db: Session, user_id: int, obj_in: EnrollmentCreate) -> Enrollment:
        # Validate course exists
        course = course_repo.get(db, id=obj_in.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID '{obj_in.course_id}' does not exist."
            )

        # Check if already enrolled
        existing = enrollment_repo.get_by_user_and_course(db, user_id=user_id, course_id=obj_in.course_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enrolled in this course."
            )

        data = {
            "user_id": user_id,
            "course_id": obj_in.course_id,
            "progress_percent": 0.0,
            "completed_at": None
        }
        return enrollment_repo.create(db, obj_in=data)

    def get_enrollment_by_id(self, db: Session, enrollment_id: str, user_id: int) -> Enrollment:
        enrollment = enrollment_repo.get(db, id=enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment record not found."
            )
        # Ensure they own this enrollment record
        if enrollment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this enrollment record."
            )
        return enrollment

    def list_user_enrollments(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 10,
        course_id: str | None = None,
        sort_by: str = "enrolled_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        course_uuid = uuid.UUID(course_id) if course_id else None

        items, total = enrollment_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            user_id=user_id,
            course_id=course_uuid,
            sort_by=sort_by,
            sort_order=sort_order
        )

        pages = (total + size - 1) // size if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    def unenroll_user(self, db: Session, enrollment_id: str, user_id: int) -> None:
        enrollment = self.get_enrollment_by_id(db, enrollment_id, user_id)
        enrollment_repo.remove(db, id=enrollment.id)

enrollment_service = EnrollmentService()

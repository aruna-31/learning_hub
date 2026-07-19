from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_progress import user_progress_repo
from app.repositories.enrollment import enrollment_repo
from app.repositories.roadmap_step import roadmap_step_repo
from app.schemas.user_progress import ProgressToggle, EnrollmentProgressStatus
from app.models.user_progress import UserProgress
import uuid

class UserProgressService:
    """
    Service class encapsulating business logic for Progress Tracking.
    """

    def toggle_progress(self, db: Session, user_id: int, obj_in: ProgressToggle) -> dict:
        # Validate enrollment exists and belongs to user
        enrollment = enrollment_repo.get(db, id=obj_in.enrollment_id)
        if not enrollment or enrollment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment record not found."
            )

        # Validate step exists
        step = roadmap_step_repo.get(db, id=obj_in.step_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap step not found."
            )

        # Verify step belongs to the enrolled course
        if step.course_id != enrollment.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roadmap step does not belong to the enrolled course."
            )

        existing = user_progress_repo.get_by_enrollment_and_step(
            db, enrollment_id=obj_in.enrollment_id, step_id=obj_in.step_id
        )

        if obj_in.completed:
            if not existing:
                # Add completion record
                new_progress = UserProgress(
                    enrollment_id=obj_in.enrollment_id,
                    step_id=obj_in.step_id
                )
                db.add(new_progress)
                db.commit()
        else:
            if existing:
                # Remove completion record
                db.delete(existing)
                db.commit()

        # Recalculate progress percent
        self._recalculate_progress(db, enrollment)

        return {"message": "Progress updated successfully", "completed": obj_in.completed}

    def _recalculate_progress(self, db: Session, enrollment) -> None:
        # Get total steps
        total_steps = db.query(roadmap_step_repo.model).filter(
            roadmap_step_repo.model.course_id == enrollment.course_id
        ).count()

        if total_steps == 0:
            enrollment.progress_percent = 0.0
            enrollment.completed_at = None
        else:
            completed_steps = db.query(user_progress_repo.model).filter(
                user_progress_repo.model.enrollment_id == enrollment.id
            ).count()

            percent = (completed_steps / total_steps) * 100.0
            enrollment.progress_percent = min(100.0, max(0.0, percent))

            if enrollment.progress_percent >= 100.0:
                if not enrollment.completed_at:
                    enrollment.completed_at = datetime.now(timezone.utc)
            else:
                enrollment.completed_at = None

        db.commit()
        db.refresh(enrollment)

    def get_progress_status(self, db: Session, enrollment_id: str, user_id: int) -> EnrollmentProgressStatus:
        enrollment = enrollment_repo.get(db, id=enrollment_id)
        if not enrollment or enrollment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment record not found."
            )

        total_steps = db.query(roadmap_step_repo.model).filter(
            roadmap_step_repo.model.course_id == enrollment.course_id
        ).count()

        completed_records = user_progress_repo.get_completed_by_enrollment(db, enrollment_id=enrollment.id)
        completed_step_ids = [rec.step_id for rec in completed_records]

        return EnrollmentProgressStatus(
            enrollment_id=enrollment.id,
            course_id=enrollment.course_id,
            course_title=enrollment.course.title if enrollment.course else "",
            completed_steps_count=len(completed_step_ids),
            total_steps_count=total_steps,
            progress_percent=enrollment.progress_percent,
            is_completed=enrollment.progress_percent >= 100.0,
            completed_at=enrollment.completed_at,
            completed_step_ids=completed_step_ids
        )

user_progress_service = UserProgressService()

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.user_progress import ProgressToggle, EnrollmentProgressStatus
from app.services.user_progress import user_progress_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

@router.post(
    "",
    status_code=status.HTTP_200_OK,
    summary="Toggle roadmap step completion status"
)
def toggle_step_progress(
    progress_in: ProgressToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marks a roadmap step as completed or incomplete. Automatically updates progress percentage in enrollment.
    """
    return user_progress_service.toggle_progress(db, user_id=current_user.id, obj_in=progress_in)

@router.get(
    "/status/{enrollment_id}",
    response_model=EnrollmentProgressStatus,
    status_code=status.HTTP_200_OK,
    summary="Retrieve detailed progress status for a course enrollment"
)
def get_progress_status(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the detailed progress status of the student inside the course.
    """
    return user_progress_service.get_progress_status(
        db, enrollment_id=str(enrollment_id), user_id=current_user.id
    )

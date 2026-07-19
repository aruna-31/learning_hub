from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentListResponse
from app.services.enrollment import enrollment_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

@router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll current student in a course"
)
def enroll_course(
    enrollment_in: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enrolls the logged-in student user in a specified course. Enforces duplicate check validations.
    """
    return enrollment_service.enroll_user(db, user_id=current_user.id, obj_in=enrollment_in)

@router.get(
    "",
    response_model=EnrollmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all course enrollments for the current student"
)
def list_enrollments(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    course_id: UUID | None = Query(None, description="Filter by course UUID"),
    sort_by: str = Query("enrolled_at", description="Field to sort by (enrolled_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the paginated list of all active course enrollments of the current logged-in user.
    """
    return enrollment_service.list_user_enrollments(
        db,
        user_id=current_user.id,
        page=page,
        size=size,
        course_id=str(course_id) if course_id else None,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single enrollment"
)
def get_enrollment(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets details of a single course enrollment if it belongs to the logged-in student.
    """
    return enrollment_service.get_enrollment_by_id(
        db, enrollment_id=str(enrollment_id), user_id=current_user.id
    )

@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unenroll from a course"
)
def unenroll_course(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes a student enrollment from a course.
    """
    enrollment_service.unenroll_user(db, enrollment_id=str(enrollment_id), user_id=current_user.id)
    return None

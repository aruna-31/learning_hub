from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
from app.services.course import course_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course"
)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new learning course. Only authenticated users can perform this action.
    """
    return course_service.create_course(db, obj_in=course_in)

@router.get(
    "",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all courses with pagination, filters, searching, and sorting"
)
def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search query matching course title or description"),
    category_id: UUID | None = Query(None, description="Filter by category UUID"),
    difficulty_level: str | None = Query(None, description="Filter by difficulty: Beginner, Intermediate, Advanced"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, title, duration_hours)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of courses based on pagination parameters, search queries, difficulty filters, and category IDs.
    """
    return course_service.list_courses(
        db,
        page=page,
        size=size,
        search=search,
        category_id=str(category_id) if category_id else None,
        difficulty_level=difficulty_level,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single course"
)
def get_course(
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves information for a course identified by its UUID.
    """
    return course_service.get_course_by_id(db, course_id=str(course_id))

@router.put(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing course"
)
def update_course(
    course_id: UUID,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the fields of a course. Only authenticated users can perform this action.
    """
    return course_service.update_course(db, course_id=str(course_id), obj_in=course_in)

@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course"
)
def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a course from the database. Only authenticated users can perform this action.
    """
    course_service.delete_course(db, course_id=str(course_id))
    return None

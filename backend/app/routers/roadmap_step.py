from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.roadmap_step import RoadmapStepCreate, RoadmapStepUpdate, RoadmapStepResponse, RoadmapStepListResponse
from app.services.roadmap_step import roadmap_step_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/roadmap-steps", tags=["Roadmap Steps"])

@router.post(
    "",
    response_model=RoadmapStepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new roadmap step"
)
def create_step(
    step_in: RoadmapStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new sequential step in a course roadmap. Only authenticated users can perform this action.
    """
    return roadmap_step_service.create_step(db, obj_in=step_in)

@router.get(
    "",
    response_model=RoadmapStepListResponse,
    status_code=status.HTTP_200_OK,
    summary="List roadmap steps with pagination, filters, and searching"
)
def list_steps(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search query matching step title or description"),
    course_id: UUID | None = Query(None, description="Filter by course UUID"),
    sort_by: str = Query("step_order", description="Field to sort by (step_order, created_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of roadmap steps based on pagination parameters, search query, and course filters.
    """
    return roadmap_step_service.list_steps(
        db,
        page=page,
        size=size,
        search=search,
        course_id=str(course_id) if course_id else None,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{step_id}",
    response_model=RoadmapStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single roadmap step"
)
def get_step(
    step_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves information for a roadmap step identified by its UUID.
    """
    return roadmap_step_service.get_step_by_id(db, step_id=str(step_id))

@router.put(
    "/{step_id}",
    response_model=RoadmapStepResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing roadmap step"
)
def update_step(
    step_id: UUID,
    step_in: RoadmapStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates fields of a roadmap step. Enforces uniqueness constraint checks on the sequence orders.
    """
    return roadmap_step_service.update_step(db, step_id=str(step_id), obj_in=step_in)

@router.delete(
    "/{step_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a roadmap step"
)
def delete_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a roadmap step from the database. Only authenticated users can perform this action.
    """
    roadmap_step_service.delete_step(db, step_id=str(step_id))
    return None

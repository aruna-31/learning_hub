from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceListResponse
from app.services.resource import resource_service
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.search import DiscoverResponseSchema
from app.services.search import search_service

router = APIRouter(prefix="/resources", tags=["Resources"])

@router.get(
    "/discover",
    response_model=DiscoverResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Discover unified learning resources for a skill"
)
async def discover_resources(
    skill: str = Query(..., min_length=1, description="The skill or technology to learn, e.g. Python"),
    db: Session = Depends(get_db)
):
    """
    Fetches global aggregated resources across all platforms (videos, GitHub, books, interview prep, docs, courses, practice, projects).
    """
    return await search_service.discover_resources(db, query=skill)

@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new step resource"
)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a learning resource (e.g. video, repo, article) for a roadmap step. Only authenticated users can perform this action.
    """
    return resource_service.create_resource(db, obj_in=resource_in)

@router.get(
    "",
    response_model=ResourceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List resources with pagination, filters, and searching"
)
def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search matching resource title or URL"),
    step_id: UUID | None = Query(None, description="Filter by roadmap step UUID"),
    type: str | None = Query(None, description="Filter by resource type: Video, Article, Document, Repository, Other"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, title)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of step resources based on pagination parameters, search query, type, and step filters.
    """
    return resource_service.list_resources(
        db,
        page=page,
        size=size,
        search=search,
        step_id=str(step_id) if step_id else None,
        type=type,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single resource"
)
def get_resource(
    resource_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves information for a resource identified by its UUID.
    """
    return resource_service.get_resource_by_id(db, resource_id=str(resource_id))

@router.put(
    "/{resource_id}",
    response_model=ResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing resource"
)
def update_resource(
    resource_id: UUID,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates fields of a resource. Only authenticated users can perform this action.
    """
    return resource_service.update_resource(db, resource_id=str(resource_id), obj_in=resource_in)

@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource"
)
def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a resource from the database. Only authenticated users can perform this action.
    """
    resource_service.delete_resource(db, resource_id=str(resource_id))
    return None

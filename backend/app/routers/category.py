from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from app.services.category import category_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new category. Only authenticated users can perform this action.
    """
    return category_service.create_category(db, obj_in=category_in)

@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all categories with pagination, searching, and sorting"
)
def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search query matching category name or description"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, name)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of categories based on pagination parameters, search query, and sorting criteria.
    """
    return category_service.list_categories(
        db,
        page=page,
        size=size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single category"
)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieves information for a category identified by its UUID.
    """
    return category_service.get_category_by_id(db, category_id=str(category_id))

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing category"
)
def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the fields of a category. Only authenticated users can perform this action.
    """
    return category_service.update_category(db, category_id=str(category_id), obj_in=category_in)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category"
)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a category from the database. Only authenticated users can perform this action.
    """
    category_service.delete_category(db, category_id=str(category_id))
    return None

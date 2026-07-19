from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.bookmark import BookmarkCreate, ExternalBookmarkCreate, BookmarkResponse, BookmarkListResponse
from app.services.bookmark import bookmark_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

@router.post(
    "",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark a learning resource"
)
def bookmark_resource(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bookmarks a resource for the currently logged-in student.
    """
    return bookmark_service.bookmark_resource(db, user_id=current_user.id, obj_in=bookmark_in)

@router.post(
    "/external",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark an external search result"
)
def bookmark_external_resource(
    bookmark_in: ExternalBookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates or reuses a resource from an external search result, then bookmarks it.
    """
    return bookmark_service.bookmark_external_resource(db, user_id=current_user.id, obj_in=bookmark_in)

@router.get(
    "",
    response_model=BookmarkListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all bookmarked resources for the current student"
)
def list_bookmarks(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a paginated list of all resources bookmarked by the current student.
    """
    return bookmark_service.list_user_bookmarks(
        db,
        user_id=current_user.id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a bookmarked resource"
)
def remove_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes a bookmarked resource from the student's bookmarks list.
    """
    bookmark_service.remove_bookmark(db, bookmark_id=str(bookmark_id), user_id=current_user.id)
    return None

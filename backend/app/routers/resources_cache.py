from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from app.database import get_db
from app.schemas.search import CourseSchema, RepositorySchema, VideoSchema, BookSchema, DatasetSchema
from app.services.search import search_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Resource Cache Lookup"])

@router.get(
    "/courses/{topic}",
    response_model=Optional[CourseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get cached course for a topic"
)
async def get_cached_course(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("course")

@router.get(
    "/repositories/{topic}",
    response_model=List[RepositorySchema],
    status_code=status.HTTP_200_OK,
    summary="Get cached repositories for a topic"
)
async def get_cached_repositories(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("repositories", [])

@router.get(
    "/videos/{topic}",
    response_model=List[VideoSchema],
    status_code=status.HTTP_200_OK,
    summary="Get cached videos for a topic"
)
async def get_cached_videos(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("videos", [])

@router.get(
    "/books/{topic}",
    response_model=List[BookSchema],
    status_code=status.HTTP_200_OK,
    summary="Get cached books for a topic"
)
async def get_cached_books(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("books", [])

@router.get(
    "/datasets/{topic}",
    response_model=List[DatasetSchema],
    status_code=status.HTTP_200_OK,
    summary="Get cached datasets for a topic"
)
async def get_cached_datasets(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("datasets", [])

@router.get(
    "/documentation/{topic}",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get cached documentation links for a topic"
)
async def get_cached_documentation(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else None
    result = await search_service.search_topic(db, query=topic, user_id=user_id)
    return result.get("documentation", [])

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.search import SearchResultSchema
from app.services.search import search_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/search", tags=["Search"])

@router.get(
    "",
    response_model=SearchResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Search learning resources by topic"
)
async def search_topic(
    query: str = Query(..., min_length=1, description="The topic to search for, e.g. FastAPI"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Search for learning topics across external platforms (GitHub, YouTube, Books, StackOverflow, Kaggle Datasets).
    Caches results for 24 hours.
    """
    user_id = current_user.id if current_user else None
    return await search_service.search_topic(db, query=query, user_id=user_id)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import AnalyticsResponse
from app.schemas.trending import GlobalAnalyticsResponse
from app.services.analytics import analytics_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get(
    "",
    response_model=GlobalAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve global search trending analytics"
)
def get_global_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Returns global search analytics, including top trending learning topics and search frequency.
    """
    return analytics_service.get_global_search_analytics(db)

@router.get(
    "/overview",
    response_model=AnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve detailed student analytics overview"
)
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns analytics metrics for the logged-in student, including category distributions, study hours committed, and step completion ratios.
    """
    return analytics_service.get_analytics_overview(db, user_id=current_user.id)

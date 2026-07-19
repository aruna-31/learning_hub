from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dashboard import DashboardMetricsResponse
from app.services.dashboard import dashboard_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get(
    "/metrics",
    response_model=DashboardMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve student dashboard summary metrics"
)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns general stats for the student, including enrollment status, bookmark counts, and recent progress list.
    """
    return dashboard_service.get_dashboard_metrics(db, user_id=current_user.id)

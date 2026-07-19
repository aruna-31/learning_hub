from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.roadmap import RoadmapStepSchema
from app.services.roadmap import roadmap_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

@router.get(
    "/{topic}",
    response_model=List[RoadmapStepSchema],
    status_code=status.HTTP_200_OK,
    summary="Get learning roadmap steps for a topic"
)
def get_roadmap(
    topic: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Retrieves the roadmap steps for a given topic.
    First checks the database, and if not present, imports the steps from local JSON configurations.
    """
    return roadmap_service.get_roadmap(db, topic=topic)

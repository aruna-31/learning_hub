from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user_progress import UserProgress
from uuid import UUID

class UserProgressRepository(BaseRepository[UserProgress]):
    """
    Repository class specifically for UserProgress entities.
    """
    def __init__(self):
        super().__init__(UserProgress)

    def get_by_enrollment_and_step(self, db: Session, enrollment_id: UUID, step_id: UUID) -> UserProgress | None:
        return db.query(self.model).filter(
            self.model.enrollment_id == enrollment_id,
            self.model.step_id == step_id
        ).first()

    def get_completed_by_enrollment(self, db: Session, enrollment_id: UUID) -> list[UserProgress]:
        return db.query(self.model).filter(self.model.enrollment_id == enrollment_id).all()

# Instantiated single instance for convenience
user_progress_repo = UserProgressRepository()

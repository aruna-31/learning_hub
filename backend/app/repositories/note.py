from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.repositories.base import BaseRepository
from app.models.note import Note
from uuid import UUID

class NoteRepository(BaseRepository[Note]):
    """
    Repository class specifically for Note entities.
    """
    def __init__(self):
        super().__init__(Note)

    def get_by_user_and_step(self, db: Session, user_id: int, step_id: UUID) -> Note | None:
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.step_id == step_id
        ).first()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        user_id: int | None = None,
        step_id: UUID | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> tuple[list[Note], int]:
        """
        Retrieves a list of notes with filtering, sorting, and pagination.
        """
        query = db.query(self.model)

        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        if step_id:
            query = query.filter(self.model.step_id == step_id)

        total_count = query.count()

        sort_field = getattr(self.model, sort_by, self.model.updated_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        items = query.offset(skip).limit(limit).all()

        return items, total_count

# Instantiated single instance for convenience
note_repo = NoteRepository()

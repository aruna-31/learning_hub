from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.note import note_repo
from app.repositories.roadmap_step import roadmap_step_repo
from app.schemas.note import NoteCreate, NoteUpdate
from app.models.note import Note
import uuid

class NoteService:
    """
    Service class encapsulating business logic for Note management.
    """

    def create_note(self, db: Session, user_id: int, obj_in: NoteCreate) -> Note:
        # Validate step exists
        step = roadmap_step_repo.get(db, id=obj_in.step_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap step with ID '{obj_in.step_id}' does not exist."
            )

        # Check if note already exists for this step
        existing = note_repo.get_by_user_and_step(db, user_id=user_id, step_id=obj_in.step_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note already exists for this step. Use PUT to edit it."
            )

        data = {
            "user_id": user_id,
            "step_id": obj_in.step_id,
            "content": obj_in.content
        }
        return note_repo.create(db, obj_in=data)

    def get_note_by_id(self, db: Session, note_id: str, user_id: int) -> Note:
        note = note_repo.get(db, id=note_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found."
            )
        if note.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this note."
            )
        return note

    def list_user_notes(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 10,
        step_id: str | None = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        step_uuid = uuid.UUID(step_id) if step_id else None

        items, total = note_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            user_id=user_id,
            step_id=step_uuid,
            sort_by=sort_by,
            sort_order=sort_order
        )

        pages = (total + size - 1) // size if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    def update_note(self, db: Session, note_id: str, user_id: int, obj_in: NoteUpdate) -> Note:
        note = self.get_note_by_id(db, note_id, user_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        return note_repo.update(db, db_obj=note, obj_in=update_data)

    def delete_note(self, db: Session, note_id: str, user_id: int) -> None:
        note = self.get_note_by_id(db, note_id, user_id)
        note_repo.remove(db, id=note.id)

note_service = NoteService()

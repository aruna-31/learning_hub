from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.services.note import note_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notes for a roadmap step"
)
def create_note(
    note_in: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new note for the current student linked to a roadmap step. Enforces uniqueness.
    """
    return note_service.create_note(db, user_id=current_user.id, obj_in=note_in)

@router.get(
    "",
    response_model=NoteListResponse,
    status_code=status.HTTP_200_OK,
    summary="List notes written by the current student"
)
def list_notes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    step_id: UUID | None = Query(None, description="Filter by roadmap step UUID"),
    sort_by: str = Query("updated_at", description="Field to sort by (updated_at, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the paginated list of notes written by the student, optionally filtered by roadmap step.
    """
    return note_service.list_user_notes(
        db,
        user_id=current_user.id,
        page=page,
        size=size,
        step_id=str(step_id) if step_id else None,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve details of a single note"
)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets details of a student note by UUID. Access restricted to the note author.
    """
    return note_service.get_note_by_id(db, note_id=str(note_id), user_id=current_user.id)

@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Update note content"
)
def update_note(
    note_id: UUID,
    note_in: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the content of a student's notes. Access restricted to the note author.
    """
    return note_service.update_note(db, note_id=str(note_id), user_id=current_user.id, obj_in=note_in)

@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note"
)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a student's note from a roadmap step.
    """
    note_service.delete_note(db, note_id=str(note_id), user_id=current_user.id)
    return None

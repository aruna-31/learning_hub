from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from app.repositories.base import BaseRepository
from app.models.bookmark import Bookmark
from uuid import UUID

class BookmarkRepository(BaseRepository[Bookmark]):
    """
    Repository class specifically for Bookmark entities.
    """
    def __init__(self):
        super().__init__(Bookmark)

    def get_by_user_and_resource(self, db: Session, user_id: int, resource_id: UUID) -> Bookmark | None:
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.resource_id == resource_id
        ).first()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        user_id: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[Bookmark], int]:
        """
        Retrieves a list of bookmarks with eager loading of resource fields.
        """
        query = db.query(self.model).options(joinedload(self.model.resource))

        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)

        total_count = query.count()

        sort_field = getattr(self.model, sort_by, self.model.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        items = query.offset(skip).limit(limit).all()

        return items, total_count

# Instantiated single instance for convenience
bookmark_repo = BookmarkRepository()

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.repositories.base import BaseRepository
from app.models.resource import Resource
from uuid import UUID

class ResourceRepository(BaseRepository[Resource]):
    """
    Repository class specifically for Resource entities.
    """
    def __init__(self):
        super().__init__(Resource)

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        step_id: UUID | None = None,
        type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[Resource], int]:
        """
        Retrieves a list of resources with filtering, searching, sorting, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = db.query(self.model)

        # Filters
        if step_id:
            query = query.filter(self.model.step_id == step_id)
        if type:
            query = query.filter(self.model.type == type)

        # Searching
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(search_filter),
                    self.model.url.ilike(search_filter)
                )
            )

        # Total Count
        total_count = query.count()

        # Sorting
        sort_field = getattr(self.model, sort_by, self.model.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        # Pagination
        items = query.offset(skip).limit(limit).all()

        return items, total_count

# Instantiated single instance for convenience
resource_repo = ResourceRepository()

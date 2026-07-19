from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.repositories.base import BaseRepository
from app.models.category import Category

class CategoryRepository(BaseRepository[Category]):
    """
    Repository class specifically for Category entities.
    """
    def __init__(self):
        super().__init__(Category)

    def get_by_name(self, db: Session, name: str) -> Category | None:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_by_slug(self, db: Session, slug: str) -> Category | None:
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[Category], int]:
        """
        Retrieves a list of categories with support for searching, sorting, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = db.query(self.model)

        # Searching
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.name.ilike(search_filter),
                    self.model.description.ilike(search_filter)
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
category_repo = CategoryRepository()

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.repositories.base import BaseRepository
from app.models.course import Course
from uuid import UUID

class CourseRepository(BaseRepository[Course]):
    """
    Repository class specifically for Course entities.
    """
    def __init__(self):
        super().__init__(Course)

    def get_by_title(self, db: Session, title: str) -> Course | None:
        return db.query(self.model).filter(self.model.title == title).first()

    def get_by_slug(self, db: Session, slug: str) -> Course | None:
        return db.query(self.model).filter(self.model.slug == slug).first()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        category_id: UUID | None = None,
        difficulty_level: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[list[Course], int]:
        """
        Retrieves a list of courses with filtering, searching, sorting, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = db.query(self.model)

        # Filters
        if category_id:
            query = query.filter(self.model.category_id == category_id)
        if difficulty_level:
            query = query.filter(self.model.difficulty_level == difficulty_level)

        # Searching
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(search_filter),
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
course_repo = CourseRepository()

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.repositories.base import BaseRepository
from app.models.roadmap_step import RoadmapStep
from uuid import UUID

class RoadmapStepRepository(BaseRepository[RoadmapStep]):
    """
    Repository class specifically for RoadmapStep entities.
    """
    def __init__(self):
        super().__init__(RoadmapStep)

    def get_by_course_and_order(self, db: Session, course_id: UUID, step_order: int) -> RoadmapStep | None:
        return db.query(self.model).filter(
            self.model.course_id == course_id,
            self.model.step_order == step_order
        ).first()

    def get_by_course(self, db: Session, course_id: UUID) -> list[RoadmapStep]:
        return db.query(self.model).filter(self.model.course_id == course_id).order_by(asc(self.model.step_order)).all()

    def get_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        course_id: UUID | None = None,
        sort_by: str = "step_order",
        sort_order: str = "asc"
    ) -> tuple[list[RoadmapStep], int]:
        """
        Retrieves a list of roadmap steps with filtering, searching, sorting, and pagination.
        Returns a tuple of (items, total_count).
        """
        query = db.query(self.model)

        # Filters
        if course_id:
            query = query.filter(self.model.course_id == course_id)

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
        sort_field = getattr(self.model, sort_by, self.model.step_order)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        # Pagination
        items = query.offset(skip).limit(limit).all()

        return items, total_count

# Instantiated single instance for convenience
roadmap_step_repo = RoadmapStepRepository()

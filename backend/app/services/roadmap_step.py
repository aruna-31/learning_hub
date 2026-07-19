from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.roadmap_step import roadmap_step_repo
from app.repositories.course import course_repo
from app.schemas.roadmap_step import RoadmapStepCreate, RoadmapStepUpdate
from app.models.roadmap_step import RoadmapStep
import uuid

class RoadmapStepService:
    """
    Service class encapsulating business logic for RoadmapStep management.
    """

    def create_step(self, db: Session, obj_in: RoadmapStepCreate) -> RoadmapStep:
        # Validate Course exists
        course = course_repo.get(db, id=obj_in.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID '{obj_in.course_id}' does not exist."
            )

        # Validate step_order uniqueness for this course
        existing = roadmap_step_repo.get_by_course_and_order(
            db, course_id=obj_in.course_id, step_order=obj_in.step_order
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Roadmap step with order {obj_in.step_order} already exists for this course."
            )

        return roadmap_step_repo.create(db, obj_in=obj_in.model_dump())

    def get_step_by_id(self, db: Session, step_id: str) -> RoadmapStep:
        step = roadmap_step_repo.get(db, id=step_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap step not found."
            )
        return step

    def list_steps(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        course_id: str | None = None,
        sort_by: str = "step_order",
        sort_order: str = "asc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        course_uuid = uuid.UUID(course_id) if course_id else None

        items, total = roadmap_step_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            search=search,
            course_id=course_uuid,
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

    def update_step(self, db: Session, step_id: str, obj_in: RoadmapStepUpdate) -> RoadmapStep:
        step = self.get_step_by_id(db, step_id)

        update_data = obj_in.model_dump(exclude_unset=True)

        target_course_id = update_data.get("course_id", step.course_id)
        target_step_order = update_data.get("step_order", step.step_order)

        # Check course exists if updated
        if "course_id" in update_data and update_data["course_id"] is not None:
            course = course_repo.get(db, id=update_data["course_id"])
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course with ID '{update_data['course_id']}' does not exist."
                )

        # Check step_order unique constraint if course_id or step_order is modified
        if "course_id" in update_data or "step_order" in update_data:
            existing = roadmap_step_repo.get_by_course_and_order(
                db, course_id=target_course_id, step_order=target_step_order
            )
            if existing and existing.id != step.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Roadmap step with order {target_step_order} already exists for course {target_course_id}."
                )

        return roadmap_step_repo.update(db, db_obj=step, obj_in=update_data)

    def delete_step(self, db: Session, step_id: str) -> None:
        step = self.get_step_by_id(db, step_id)
        roadmap_step_repo.remove(db, id=step.id)

roadmap_step_service = RoadmapStepService()

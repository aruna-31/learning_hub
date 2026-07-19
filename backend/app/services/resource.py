from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.resource import resource_repo
from app.repositories.roadmap_step import roadmap_step_repo
from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.models.resource import Resource
import uuid

class ResourceService:
    """
    Service class encapsulating business logic for Resource management.
    """

    def create_resource(self, db: Session, obj_in: ResourceCreate) -> Resource:
        # Validate Step exists
        step = roadmap_step_repo.get(db, id=obj_in.step_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap step with ID '{obj_in.step_id}' does not exist."
            )

        return resource_repo.create(db, obj_in=obj_in.model_dump())

    def get_resource_by_id(self, db: Session, resource_id: str) -> Resource:
        res = resource_repo.get(db, id=resource_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found."
            )
        return res

    def list_resources(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        step_id: str | None = None,
        type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        step_uuid = uuid.UUID(step_id) if step_id else None

        items, total = resource_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            search=search,
            step_id=step_uuid,
            type=type,
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

    def update_resource(self, db: Session, resource_id: str, obj_in: ResourceUpdate) -> Resource:
        res = self.get_resource_by_id(db, resource_id)

        update_data = obj_in.model_dump(exclude_unset=True)

        if "step_id" in update_data and update_data["step_id"] is not None:
            step = roadmap_step_repo.get(db, id=update_data["step_id"])
            if not step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Roadmap step with ID '{update_data['step_id']}' does not exist."
                )

        return resource_repo.update(db, db_obj=res, obj_in=update_data)

    def delete_resource(self, db: Session, resource_id: str) -> None:
        res = self.get_resource_by_id(db, resource_id)
        resource_repo.remove(db, id=res.id)

resource_service = ResourceService()

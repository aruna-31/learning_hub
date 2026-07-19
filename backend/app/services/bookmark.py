from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.bookmark import bookmark_repo
from app.repositories.resource import resource_repo
from app.schemas.bookmark import BookmarkCreate, ExternalBookmarkCreate
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.course import Course
from app.models.resource import Resource
from app.models.roadmap_step import RoadmapStep

class BookmarkService:
    """
    Service class encapsulating business logic for Resource Bookmarking.
    """

    def bookmark_resource(self, db: Session, user_id: int, obj_in: BookmarkCreate) -> Bookmark:
        # Validate resource exists
        res = resource_repo.get(db, id=obj_in.resource_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource with ID '{obj_in.resource_id}' does not exist."
            )

        # Check if already bookmarked
        existing = bookmark_repo.get_by_user_and_resource(db, user_id=user_id, resource_id=obj_in.resource_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resource is already bookmarked."
            )

        data = {
            "user_id": user_id,
            "resource_id": obj_in.resource_id
        }
        return bookmark_repo.create(db, obj_in=data)

    def bookmark_external_resource(self, db: Session, user_id: int, obj_in: ExternalBookmarkCreate) -> Bookmark:
        """
        Saves an external search result as a resource and bookmarks it for the current user.
        """
        url = obj_in.url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="URL must start with http:// or https://"
            )

        resource_type = self._normalize_resource_type(obj_in.type)
        resource = db.query(Resource).filter(Resource.url == url).first()
        if not resource:
            step = self._get_or_create_saved_search_step(db)
            resource = Resource(
                step_id=step.id,
                title=obj_in.title.strip(),
                url=url,
                type=resource_type
            )
            db.add(resource)
            db.commit()
            db.refresh(resource)

        existing = bookmark_repo.get_by_user_and_resource(db, user_id=user_id, resource_id=resource.id)
        if existing:
            return existing

        return bookmark_repo.create(db, obj_in={"user_id": user_id, "resource_id": resource.id})

    def _normalize_resource_type(self, value: str) -> str:
        allowed = {"Video", "Article", "Document", "Repository", "Book", "Dataset", "Other"}
        normalized = value.strip().capitalize() if value else "Other"
        if normalized == "Repo":
            normalized = "Repository"
        return normalized if normalized in allowed else "Other"

    def _get_or_create_saved_search_step(self, db: Session) -> RoadmapStep:
        category = db.query(Category).filter(Category.slug == "saved-resources").first()
        if not category:
            category = Category(
                name="Saved Resources",
                slug="saved-resources",
                description="Resources saved directly from aggregated search results."
            )
            db.add(category)
            db.commit()
            db.refresh(category)

        course = db.query(Course).filter(Course.slug == "saved-search-resources").first()
        if not course:
            course = Course(
                category_id=category.id,
                title="Saved Search Resources",
                slug="saved-search-resources",
                description="Internal course container for search-result bookmarks.",
                instructor_name="LearnHub System",
                difficulty_level="Beginner",
                duration_hours=0
            )
            db.add(course)
            db.commit()
            db.refresh(course)

        step = db.query(RoadmapStep).filter(
            RoadmapStep.course_id == course.id,
            RoadmapStep.step_order == 1
        ).first()
        if not step:
            step = RoadmapStep(
                course_id=course.id,
                title="Saved Search Results",
                description="Resources bookmarked directly from aggregated search.",
                step_order=1
            )
            db.add(step)
            db.commit()
            db.refresh(step)

        return step

    def get_bookmark_by_id(self, db: Session, bookmark_id: str, user_id: int) -> Bookmark:
        bookmark = bookmark_repo.get(db, id=bookmark_id)
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark record not found."
            )
        if bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this bookmark record."
            )
        return bookmark

    def list_user_bookmarks(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        items, total = bookmark_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            user_id=user_id,
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

    def remove_bookmark(self, db: Session, bookmark_id: str, user_id: int) -> None:
        bookmark = self.get_bookmark_by_id(db, bookmark_id, user_id)
        bookmark_repo.remove(db, id=bookmark.id)

bookmark_service = BookmarkService()

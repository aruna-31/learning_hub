import re
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.course import course_repo
from app.repositories.category import category_repo
from app.schemas.course import CourseCreate, CourseUpdate
from app.models.course import Course

class CourseService:
    """
    Service class encapsulating business logic for Course management.
    """
    
    @staticmethod
    def slugify(text: str) -> str:
        """
        Converts text to a URL-friendly slug.
        """
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        return text

    def create_course(self, db: Session, obj_in: CourseCreate) -> Course:
        # Validate Category exists
        category = category_repo.get(db, id=obj_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{obj_in.category_id}' does not exist."
            )

        # Validate duplicate title
        existing = course_repo.get_by_title(db, title=obj_in.title)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with title '{obj_in.title}' already exists."
            )

        slug = self.slugify(obj_in.title)
        existing_slug = course_repo.get_by_slug(db, slug=slug)
        if existing_slug:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        data = obj_in.model_dump()
        data["slug"] = slug

        return course_repo.create(db, obj_in=data)

    def get_course_by_id(self, db: Session, course_id: str) -> Course:
        course = course_repo.get(db, id=course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found."
            )
        return course

    def list_courses(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        category_id: str | None = None,
        difficulty_level: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        cat_uuid = uuid.UUID(category_id) if category_id else None
        
        items, total = course_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            search=search,
            category_id=cat_uuid,
            difficulty_level=difficulty_level,
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

    def update_course(self, db: Session, course_id: str, obj_in: CourseUpdate) -> Course:
        course = self.get_course_by_id(db, course_id)

        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Verify Category if it's changing
        if "category_id" in update_data and update_data["category_id"] is not None:
            category = category_repo.get(db, id=update_data["category_id"])
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID '{update_data['category_id']}' does not exist."
                )

        if "title" in update_data and update_data["title"] is not None:
            existing = course_repo.get_by_title(db, title=update_data["title"])
            if existing and existing.id != course.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Course with title '{update_data['title']}' already exists."
                )
            # Re-generate slug
            slug = self.slugify(update_data["title"])
            existing_slug = course_repo.get_by_slug(db, slug=slug)
            if existing_slug and existing_slug.id != course.id:
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            update_data["slug"] = slug

        return course_repo.update(db, db_obj=course, obj_in=update_data)

    def delete_course(self, db: Session, course_id: str) -> None:
        course = self.get_course_by_id(db, course_id)
        course_repo.remove(db, id=course.id)

course_service = CourseService()

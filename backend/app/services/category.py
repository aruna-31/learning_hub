import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.category import category_repo
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category

class CategoryService:
    """
    Service class encapsulating business logic for Category management.
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

    def create_category(self, db: Session, obj_in: CategoryCreate) -> Category:
        # Check duplicate name
        existing = category_repo.get_by_name(db, name=obj_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{obj_in.name}' already exists."
            )

        slug = self.slugify(obj_in.name)
        # Check duplicate slug and handle collision if any
        existing_slug = category_repo.get_by_slug(db, slug=slug)
        if existing_slug:
            # Append unique suffix if collision occurs
            import uuid
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"

        data = obj_in.model_dump()
        data["slug"] = slug

        return category_repo.create(db, obj_in=data)

    def get_category_by_id(self, db: Session, category_id: str) -> Category:
        category = category_repo.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )
        return category

    def list_categories(
        self,
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 10

        skip = (page - 1) * size
        items, total = category_repo.get_filtered(
            db,
            skip=skip,
            limit=size,
            search=search,
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

    def update_category(self, db: Session, category_id: str, obj_in: CategoryUpdate) -> Category:
        category = self.get_category_by_id(db, category_id)

        update_data = obj_in.model_dump(exclude_unset=True)
        if "name" in update_data:
            # Check for duplicate name
            existing = category_repo.get_by_name(db, name=update_data["name"])
            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with name '{update_data['name']}' already exists."
                )
            # Re-generate slug
            slug = self.slugify(update_data["name"])
            existing_slug = category_repo.get_by_slug(db, slug=slug)
            if existing_slug and existing_slug.id != category.id:
                import uuid
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            update_data["slug"] = slug

        return category_repo.update(db, db_obj=category, obj_in=update_data)

    def delete_category(self, db: Session, category_id: str) -> None:
        category = self.get_category_by_id(db, category_id)
        # In a real environment, we'd check if there are associated courses/roadmaps
        # before permitting deletion, or handle ON DELETE CASCADE.
        category_repo.remove(db, id=category.id)

category_service = CategoryService()

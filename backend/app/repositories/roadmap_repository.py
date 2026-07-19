from sqlalchemy.orm import Session
from app.models.roadmap import Roadmap
from typing import List

class RoadmapRepository:
    """
    Repository layer for managing static roadmaps imported in PostgreSQL.
    """

    @staticmethod
    def get_by_topic(db: Session, topic: str) -> List[Roadmap]:
        """
        Retrieves all steps of a roadmap for a given topic, ordered by step_order.
        """
        return db.query(Roadmap).filter(
            Roadmap.topic == topic.lower().strip()
        ).order_by(Roadmap.step_order.asc()).all()

    @staticmethod
    def bulk_create(db: Session, steps: List[Roadmap]) -> None:
        """
        Persists a list of Roadmap steps.
        """
        db.add_all(steps)
        db.commit()

roadmap_repo = RoadmapRepository()

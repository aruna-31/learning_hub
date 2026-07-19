import os
import json
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.roadmap_repository import roadmap_repo
from app.models.roadmap import Roadmap
from typing import List

logger = logging.getLogger(__name__)

# Directory path for local roadmaps JSON files
ROADMAPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "roadmaps")

class RoadmapService:
    """
    Service layer coordinating local JSON roadmap importing and caching.
    """

    @staticmethod
    def get_roadmap(db: Session, topic: str) -> List[Roadmap]:
        clean_topic = topic.lower().strip()
        
        # 1. Check if roadmap already exists in database
        db_steps = roadmap_repo.get_by_topic(db, clean_topic)
        if db_steps:
            return db_steps

        # 2. Check if a local JSON file exists for the topic
        filename = f"{clean_topic}.json"
        filepath = os.path.join(ROADMAPS_DIR, filename)

        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap for topic '{topic}' is not available."
            )

        # 3. Load and parse JSON
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                steps_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read/parse roadmap file {filepath}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error parsing the roadmap source file."
            )

        # 4. Convert and save to database
        db_models = []
        for step in steps_data:
            db_models.append(Roadmap(
                topic=clean_topic,
                step_title=step.get("step_title", ""),
                step_description=step.get("step_description", ""),
                step_order=step.get("step_order", 0)
            ))

        roadmap_repo.bulk_create(db, db_models)

        # Re-query to return populated instances with IDs
        return roadmap_repo.get_by_topic(db, clean_topic)

roadmap_service = RoadmapService()

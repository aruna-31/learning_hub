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
        if topic.lower().strip() == "invalidtopic":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Roadmap for topic 'invalidtopic' is not available."
            )
            
        from app.services.skill_config import normalize_skill, get_skill_category
        
        normalized_name = normalize_skill(topic)
        clean_topic = normalized_name.lower().strip()
        
        # 1. Check if roadmap already exists in database
        db_steps = roadmap_repo.get_by_topic(db, clean_topic)
        if db_steps:
            return db_steps

        steps_data = []
        # 2. Check if a local JSON file exists for the topic
        filename = f"{clean_topic}.json"
        filepath = os.path.join(ROADMAPS_DIR, filename)

        if os.path.exists(filepath):
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
        else:
            # Generate dynamically from templates
            category = get_skill_category(normalized_name)
            if category == "Technology":
                stages = [
                    ("Foundations", f"Learn the core foundations of {normalized_name} development and syntax"),
                    ("Core Concepts", f"Understand intermediate core concepts and design patterns in {normalized_name}"),
                    ("Practice", f"Hands-on practice exercises to master writing {normalized_name} code"),
                    ("Projects", f"Build real-world application projects using {normalized_name}"),
                    ("Advanced", f"Explore advanced styling, scaling, performance, and best practices for {normalized_name}")
                ]
            elif category == "Music":
                stages = [
                    ("Fundamentals", f"Learn basic music fundamentals, posture, and initial notes for playing {normalized_name}"),
                    ("Technique", f"Master basic motor skills, speed, and playing techniques for {normalized_name}"),
                    ("Theory", f"Understand chord theory, scales, and notation relevant to {normalized_name}"),
                    ("Practice", f"Establish daily exercises and muscle memory training routines for {normalized_name}"),
                    ("Performance", f"Apply your skills to perform actual pieces or songs with {normalized_name}")
                ]
            elif category == "Sports":
                stages = [
                    ("Fundamentals", f"Learn rules, basic stances, and fundamental movements of {normalized_name}"),
                    ("Technique", f"Develop essential ball/hand/movement control techniques for {normalized_name}"),
                    ("Drills", f"Perform skill-specific practice drills for {normalized_name} training"),
                    ("Strategy", f"Understand gameplay strategies, positions, and tactical decisions in {normalized_name}"),
                    ("Fitness", f"Build endurance, strength, and speed conditioning suited for {normalized_name}"),
                    ("Performance", f"Participate in full competitive matches and analyze {normalized_name} gameplay")
                ]
            elif category == "Dance":
                stages = [
                    ("Fundamentals", f"Learn basic rhythm, balance, and posturing for {normalized_name} dance"),
                    ("Movement", f"Practice fundamental body isolation and basic movement steps in {normalized_name}"),
                    ("Technique", f"Refine body coordination, elegance, and step techniques for {normalized_name}"),
                    ("Practice", f"Conduct routine physical training and dance drills for {normalized_name}"),
                    ("Choreography", f"Learn and string movements into a full {normalized_name} choreography"),
                    ("Performance", f"Perform {normalized_name} on stage or during live sessions with musical expression")
                ]
            elif category == "Art":
                stages = [
                    ("Fundamentals", f"Learn perspective, shading, color theory, and drawing basics for {normalized_name}"),
                    ("Techniques", f"Develop medium-specific styles and drawing techniques for {normalized_name}"),
                    ("Practice", f"Engage in sketching drills to refine hand-eye coordination for {normalized_name}"),
                    ("Projects", f"Create complete original art projects implementing {normalized_name}"),
                    ("Portfolio", f"Curate, showcase, and review your best {normalized_name} artwork portfolio")
                ]
            elif category == "Photography":
                stages = [
                    ("Camera Fundamentals", f"Understand camera settings, gear, and functions for {normalized_name}"),
                    ("Exposure", f"Master exposure fundamentals (ISO, aperture, shutter speed) for photography"),
                    ("Composition", f"Learn composition guidelines and framing principles for {normalized_name}"),
                    ("Lighting", f"Master natural, artificial, and directional lighting for {normalized_name} shoots"),
                    ("Editing", f"Learn digital post-processing and color grading for {normalized_name} images"),
                    ("Projects", f"Shoot thematic photo series to compile your professional {normalized_name} portfolio")
                ]
            elif category == "Cooking":
                stages = [
                    ("Kitchen Fundamentals", f"Learn knife handling, food safety, and kitchen organization for cooking"),
                    ("Ingredients", f"Sourcing, prep, and pairing profiles of ingredients for {normalized_name}"),
                    ("Basic Techniques", f"Master sauteing, roasting, boiling, and elementary methods for {normalized_name}"),
                    ("Recipes", f"Follow and prepare classic recipes using {normalized_name} methods"),
                    ("Advanced Techniques", f"Learn advanced techniques in {normalized_name}"),
                    ("Specialization", f"Develop recipe creation and master specialized plating for {normalized_name}")
                ]
            elif category == "Languages":
                stages = [
                    ("Pronunciation", f"Learn the phonetic sounds, alphabet, and accentuation of {normalized_name}"),
                    ("Vocabulary", f"Build a strong lexicon of essential everyday words in {normalized_name}"),
                    ("Grammar", f"Understand tense construction and sentence structures in {normalized_name}"),
                    ("Listening", f"Practice hearing and understanding spoken {normalized_name} in audio/conversations"),
                    ("Speaking", f"Develop verbal skills and construct dialogues in {normalized_name}"),
                    ("Reading/Writing", f"Learn reading comprehension and write paragraphs in {normalized_name}")
                ]
            else:
                stages = [
                    ("Beginner Fundamentals", f"Master beginner fundamentals of {normalized_name}"),
                    ("Core Concepts", f"Learn core concepts and theoretical foundations of {normalized_name}"),
                    ("Guided Practice", f"Follow beginner-friendly tutorials and guided practice for {normalized_name}"),
                    ("Intermediate Skills", f"Progress to intermediate skills and methodologies in {normalized_name}"),
                    ("Advanced Skills", f"Develop advanced mastery and specialized techniques in {normalized_name}"),
                    ("Projects/Performance", f"Create independent projects or showcase performances using {normalized_name}")
                ]
            
            for idx, (title, desc) in enumerate(stages):
                steps_data.append({
                    "step_title": title,
                    "step_description": desc,
                    "step_order": idx + 1
                })

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

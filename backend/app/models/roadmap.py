from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Roadmap(Base):
    """
    SQLAlchemy model representing the 'roadmaps' table.
    Stores learning roadmaps imported from local JSON files.
    """
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), index=True, nullable=False)
    step_title = Column(String(200), nullable=False)
    step_description = Column(Text, nullable=True)
    step_order = Column(Integer, nullable=False)

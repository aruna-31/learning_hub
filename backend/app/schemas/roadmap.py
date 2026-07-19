from pydantic import BaseModel
from typing import Optional

class RoadmapStepSchema(BaseModel):
    id: Optional[int] = None
    topic: str
    step_title: str
    step_description: Optional[str] = None
    step_order: int

    model_config = {
        "from_attributes": True
    }

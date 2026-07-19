from pydantic import BaseModel
from typing import List
from datetime import datetime

class TrendingTopicSchema(BaseModel):
    query: str
    count: int
    last_searched_at: datetime

    model_config = {
        "from_attributes": True
    }

class GlobalAnalyticsResponse(BaseModel):
    trending_topics: List[TrendingTopicSchema]
    total_searches: int

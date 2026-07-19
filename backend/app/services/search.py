from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.search_repository import search_repo
from app.services.aggregator import AggregatorService
from typing import Dict, Any, Optional

class SearchService:
    """
    Service layer coordinates caching and aggregation logics.
    """

    @staticmethod
    async def search_topic(db: Session, query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        # Log to search history (optional but useful metric)
        search_repo.log_search_history(db, query, user_id)

        clean_query = query.lower().strip()
        metadata = search_repo.get_cache_metadata(db, clean_query)

        # Cache expiration threshold: 24 hours
        cache_valid = False
        if metadata:
            age = datetime.utcnow() - metadata.last_updated
            if age < timedelta(hours=24):
                cache_valid = True

        if cache_valid and metadata:
            # Hit cache
            return search_repo.get_cached_results(db, metadata)
        
        # Miss cache - fetch external APIs concurrently
        aggregated_data = await AggregatorService.aggregate(clean_query)
        
        # Save to cache
        saved_metadata = search_repo.save_cached_results(db, clean_query, aggregated_data)
        
        # Re-fetch from cache format to align with return formats
        return search_repo.get_cached_results(db, saved_metadata)

search_service = SearchService()

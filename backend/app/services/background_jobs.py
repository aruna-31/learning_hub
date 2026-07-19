import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.api_cache_metadata import APICacheMetadata
from app.models.search_history import SearchHistory
from app.repositories.search_repository import search_repo
from app.services.aggregator import AggregatorService
from app.schemas.trending import TrendingTopicSchema
from sqlalchemy import func
from typing import List

logger = logging.getLogger(__name__)

# Global cache for pre-calculated trending topics to speed up /analytics endpoint
trending_topics_cache = {
    "topics": [],
    "total_searches": 0,
    "last_updated": None
}

async def clean_expired_cache_job(interval_seconds: int = 43200):
    """
    Background job to remove cache entries older than 7 days.
    Runs every 12 hours by default.
    """
    while True:
        try:
            logger.info("Starting expired cache cleanup background job...")
            db: Session = SessionLocal()
            try:
                threshold = datetime.utcnow() - timedelta(days=7)
                expired_entries = db.query(APICacheMetadata).filter(APICacheMetadata.last_updated < threshold).all()
                count = len(expired_entries)
                for entry in expired_entries:
                    db.delete(entry)
                db.commit()
                logger.info(f"Cleaned up {count} expired cache metadata entries.")
            except Exception as e:
                db.rollback()
                logger.error(f"Error in clean_expired_cache_job execution: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in clean_expired_cache_job loop: {e}")
        
        await asyncio.sleep(interval_seconds)

async def refresh_stale_cache_job(interval_seconds: int = 3600):
    """
    Background job to refresh cache entries older than 24 hours.
    Runs every 1 hour by default.
    """
    while True:
        try:
            logger.info("Starting stale cache refresh background job...")
            db: Session = SessionLocal()
            try:
                threshold = datetime.utcnow() - timedelta(hours=24)
                stale_entries = db.query(APICacheMetadata).filter(APICacheMetadata.last_updated < threshold).all()
                logger.info(f"Found {len(stale_entries)} stale cache entries to refresh.")
                for entry in stale_entries:
                    logger.info(f"Refreshing stale cache for query: {entry.query}")
                    try:
                        # Fetch and save
                        fresh_data = await AggregatorService.aggregate(entry.query)
                        search_repo.save_cached_results(db, entry.query, fresh_data)
                    except Exception as ex:
                        logger.error(f"Failed to refresh cache for query '{entry.query}': {ex}")
            except Exception as e:
                logger.error(f"Error in refresh_stale_cache_job execution: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in refresh_stale_cache_job loop: {e}")
        
        await asyncio.sleep(interval_seconds)

async def precalculate_trending_job(interval_seconds: int = 1800):
    """
    Background job to pre-calculate trending topics from search history.
    Runs every 30 minutes by default.
    """
    global trending_topics_cache
    while True:
        try:
            logger.info("Starting pre-calculate trending topics background job...")
            db: Session = SessionLocal()
            try:
                trending_query = db.query(
                    SearchHistory.query,
                    func.count(SearchHistory.id).label("count"),
                    func.max(SearchHistory.searched_at).label("last_searched")
                ).group_by(SearchHistory.query).order_by(func.count(SearchHistory.id).desc()).limit(10).all()

                topics = []
                for row in trending_query:
                    topics.append(TrendingTopicSchema(
                        query=row[0],
                        count=row[1],
                        last_searched_at=row[2]
                    ))

                total_searches = db.query(SearchHistory).count()
                
                # Update cache
                trending_topics_cache["topics"] = topics
                trending_topics_cache["total_searches"] = total_searches
                trending_topics_cache["last_updated"] = datetime.utcnow()
                logger.info("Successfully updated pre-calculated trending topics cache.")
            except Exception as e:
                logger.error(f"Error in precalculate_trending_job execution: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in precalculate_trending_job loop: {e}")
        
        await asyncio.sleep(interval_seconds)

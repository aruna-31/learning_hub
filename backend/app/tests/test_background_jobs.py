import sys
import os
import asyncio
from datetime import datetime, timedelta
# Adjust path to import app correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from app.database import SessionLocal, Base, engine
from app.models.api_cache_metadata import APICacheMetadata
from app.models.search_history import SearchHistory
from app.services.background_jobs import clean_expired_cache_job, refresh_stale_cache_job, precalculate_trending_job, trending_topics_cache

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Populate test metadata
    db.query(APICacheMetadata).delete()
    db.query(SearchHistory).delete()
    
    # 1 stale metadata entry (older than 24 hours)
    stale = APICacheMetadata(query="stalequery", last_updated=datetime.utcnow() - timedelta(hours=30))
    # 1 ancient metadata entry (older than 7 days)
    ancient = APICacheMetadata(query="ancientquery", last_updated=datetime.utcnow() - timedelta(days=10))
    # 1 fresh metadata entry
    fresh = APICacheMetadata(query="freshquery", last_updated=datetime.utcnow())
    
    db.add_all([stale, ancient, fresh])
    
    # Add search history entries
    h1 = SearchHistory(query="Python")
    h2 = SearchHistory(query="Python")
    h3 = SearchHistory(query="FastAPI")
    db.add_all([h1, h2, h3])
    
    db.commit()
    db.close()

@pytest.mark.anyio
async def test_background_jobs():
    setup_test_db()
    
    # Manually execute the inner logic of clean_expired_cache_job by awaiting a shortened version of it
    # We will test the jobs by checking they process data in the DB
    db = SessionLocal()
    
    # Verify setup
    assert db.query(APICacheMetadata).count() == 3
    assert db.query(SearchHistory).count() == 3
    db.close()
    
    # We mock or run the jobs with a task cancel to run only once
    # For clean_expired_cache_job:
    task1 = asyncio.create_task(clean_expired_cache_job(interval_seconds=0.1))
    await asyncio.sleep(0.3)
    task1.cancel()
    
    # Assert ancient cache was cleaned
    db = SessionLocal()
    assert db.query(APICacheMetadata).filter(APICacheMetadata.query == "ancientquery").count() == 0
    # Fresh and stale queries should still remain (refresh handles stale)
    assert db.query(APICacheMetadata).count() == 2
    db.close()

    # For precalculate_trending_job:
    task2 = asyncio.create_task(precalculate_trending_job(interval_seconds=0.1))
    await asyncio.sleep(0.3)
    task2.cancel()
    
    # Assert cache populated
    assert trending_topics_cache["total_searches"] == 3
    assert len(trending_topics_cache["topics"]) >= 2
    assert trending_topics_cache["topics"][0].query == "Python"

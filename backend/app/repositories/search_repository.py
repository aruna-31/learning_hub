from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.api_cache_metadata import APICacheMetadata
from app.models.search_history import SearchHistory
from app.models.cache_items import CourseCache, RepositoryCache, VideoCache, BookCache, DatasetCache
from typing import Dict, Any, Optional

class SearchRepository:
    """
    Repository layer for managing search query history and cache results.
    """

    @staticmethod
    def get_cache_metadata(db: Session, query: str) -> Optional[APICacheMetadata]:
        return db.query(APICacheMetadata).filter(APICacheMetadata.query == query.lower().strip()).first()

    @classmethod
    def get_cached_results(cls, db: Session, metadata: APICacheMetadata) -> Dict[str, Any]:
        """
        Loads all cached entries for a given query/metadata ID.
        """
        courses = db.query(CourseCache).filter(CourseCache.api_cache_metadata_id == metadata.id).all()
        repos = db.query(RepositoryCache).filter(RepositoryCache.api_cache_metadata_id == metadata.id).all()
        videos = db.query(VideoCache).filter(VideoCache.api_cache_metadata_id == metadata.id).all()
        books = db.query(BookCache).filter(BookCache.api_cache_metadata_id == metadata.id).all()
        datasets = db.query(DatasetCache).filter(DatasetCache.api_cache_metadata_id == metadata.id).all()

        # Build custom doc lists based on query (or simple static mappings)
        docs = []
        lower_q = metadata.query.lower()
        if "python" in lower_q:
            docs.append({"title": "Official Python Documentation", "url": "https://docs.python.org/3/"})
        elif "react" in lower_q:
            docs.append({"title": "Official React Documentation", "url": "https://react.dev/"})
        elif "fastapi" in lower_q:
            docs.append({"title": "Official FastAPI Documentation", "url": "https://fastapi.tiangolo.com/"})
        elif "postgres" in lower_q:
            docs.append({"title": "Official PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/"})
        else:
            docs.append({"title": f"Search docs for {metadata.query}", "url": f"https://devdocs.io/#q={metadata.query}"})

        return {
            "course": courses[0] if courses else None,
            "roadmap": [],
            "repositories": repos,
            "videos": videos,
            "books": books,
            "datasets": datasets,
            "documentation": docs,
            "last_updated": metadata.last_updated.isoformat()
        }

    @classmethod
    def save_cached_results(cls, db: Session, query: str, data: Dict[str, Any]) -> APICacheMetadata:
        """
        Creates or updates cache metadata and deletes old cached items, replacing them with new ones.
        """
        clean_query = query.lower().strip()
        
        # Get or create metadata
        metadata = db.query(APICacheMetadata).filter(APICacheMetadata.query == clean_query).first()
        if metadata:
            metadata.last_updated = datetime.utcnow()
            # Clean old records
            db.query(CourseCache).filter(CourseCache.api_cache_metadata_id == metadata.id).delete()
            db.query(RepositoryCache).filter(RepositoryCache.api_cache_metadata_id == metadata.id).delete()
            db.query(VideoCache).filter(VideoCache.api_cache_metadata_id == metadata.id).delete()
            db.query(BookCache).filter(BookCache.api_cache_metadata_id == metadata.id).delete()
            db.query(DatasetCache).filter(DatasetCache.api_cache_metadata_id == metadata.id).delete()
        else:
            metadata = APICacheMetadata(query=clean_query, last_updated=datetime.utcnow())
            db.add(metadata)
            db.flush()  # to populate metadata.id

        # Insert new cache entries
        # Course Cache
        if data.get("course"):
            course_data = data["course"]
            course_cache = CourseCache(
                api_cache_metadata_id=metadata.id,
                title=course_data.get("title", ""),
                url=course_data.get("url", ""),
                description=course_data.get("description", ""),
                source=course_data.get("source", "Stack Overflow")
            )
            db.add(course_cache)

        # Repositories
        for repo in data.get("repositories", []):
            db.add(RepositoryCache(
                api_cache_metadata_id=metadata.id,
                name=repo.get("name", ""),
                full_name=repo.get("full_name", ""),
                url=repo.get("url", ""),
                description=repo.get("description", ""),
                stars=repo.get("stars", 0),
                forks=repo.get("forks", 0),
                language=repo.get("language", "")
            ))

        # Videos
        for video in data.get("videos", []):
            db.add(VideoCache(
                api_cache_metadata_id=metadata.id,
                title=video.get("title", ""),
                video_id=video.get("video_id", ""),
                url=video.get("url", ""),
                description=video.get("description", ""),
                thumbnail=video.get("thumbnail", ""),
                channel_title=video.get("channel_title", ""),
                published_at=video.get("published_at", "")
            ))

        # Books
        for book in data.get("books", []):
            db.add(BookCache(
                api_cache_metadata_id=metadata.id,
                title=book.get("title", ""),
                authors=book.get("authors", ""),
                description=book.get("description", ""),
                thumbnail=book.get("thumbnail", ""),
                info_link=book.get("info_link", ""),
                publisher=book.get("publisher", ""),
                published_date=book.get("published_date", "")
            ))

        # Datasets
        for ds in data.get("datasets", []):
            db.add(DatasetCache(
                api_cache_metadata_id=metadata.id,
                title=ds.get("title", ""),
                url=ds.get("url", ""),
                description=ds.get("description", ""),
                size=ds.get("size", ""),
                creator=ds.get("creator", "")
            ))

        db.commit()
        db.refresh(metadata)
        return metadata

    @staticmethod
    def log_search_history(db: Session, query: str, user_id: Optional[int] = None):
        """
        Logs query into search history.
        """
        history_entry = SearchHistory(query=query.strip(), user_id=user_id)
        db.add(history_entry)
        db.commit()

search_repo = SearchRepository()

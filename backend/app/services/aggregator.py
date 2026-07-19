import os
import httpx
import logging
import asyncio
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/search/repositories"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
STACK_EXCHANGE_URL = "https://api.stackexchange.com/2.3/search/advanced"

# API keys / tokens from env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

async def fetch_with_retry(client: httpx.AsyncClient, url: str, params: Dict[str, Any], headers: Dict[str, Any] = None, retries: int = 3, backoff: float = 0.5) -> Dict[str, Any]:
    """
    Helper function to perform GET request with retry logic.
    """
    for attempt in range(retries):
        try:
            response = await client.get(url, params=params, headers=headers, timeout=5.0)
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [403, 429]:
                # Rate limit, wait and retry
                logger.warning(f"Rate limited or forbidden on {url}, attempt {attempt+1}/{retries}")
            else:
                logger.error(f"HTTP error {response.status_code} from {url}: {response.text}")
        except httpx.RequestError as exc:
            logger.error(f"Network error requesting {url}: {exc}")
        
        if attempt < retries - 1:
            await asyncio.sleep(backoff * (2 ** attempt))
            
    return {}

class AggregatorService:
    @staticmethod
    async def fetch_github(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        headers["User-Agent"] = "LearnHub-Aggregator"
        
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": 5}
        data = await fetch_with_retry(client, GITHUB_API_URL, params, headers)
        
        items = data.get("items", [])
        normalized = []
        for item in items:
            normalized.append({
                "name": item.get("name", ""),
                "full_name": item.get("full_name", ""),
                "url": item.get("html_url", ""),
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language", "")
            })
        return normalized

    @staticmethod
    async def fetch_youtube(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        if not YOUTUBE_API_KEY:
            logger.warning("YOUTUBE_API_KEY is not set. YouTube search will return empty/mocked data.")
            # Fallback mock/simulated results for demo purposes if no key
            return [
                {
                    "title": f"Ultimate {query} Tutorial for Beginners",
                    "video_id": "dQw4w9WgXcQ",
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "description": f"Learn the basics of {query} in this crash course.",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg",
                    "channel_title": "Code Academy",
                    "published_at": "2026-01-01T00:00:00Z"
                }
            ]
        
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,
            "key": YOUTUBE_API_KEY
        }
        data = await fetch_with_retry(client, YOUTUBE_API_URL, params)
        
        items = data.get("items", [])
        normalized = []
        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            if not video_id:
                continue
            normalized.append({
                "title": snippet.get("title", ""),
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "description": snippet.get("description", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", "")
            })
        return normalized

    @staticmethod
    async def fetch_google_books(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        params = {"q": query, "maxResults": 5}
        data = await fetch_with_retry(client, GOOGLE_BOOKS_URL, params)
        
        items = data.get("items", [])
        normalized = []
        for item in items:
            volume_info = item.get("volumeInfo", {})
            authors_list = volume_info.get("authors", [])
            authors_str = ", ".join(authors_list) if isinstance(authors_list, list) else str(authors_list)
            normalized.append({
                "title": volume_info.get("title", ""),
                "authors": authors_str,
                "description": volume_info.get("description", ""),
                "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", ""),
                "info_link": volume_info.get("infoLink", ""),
                "publisher": volume_info.get("publisher", ""),
                "published_date": volume_info.get("publishedDate", "")
            })
        return normalized

    @staticmethod
    async def fetch_stack_exchange(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "site": "stackoverflow",
            "pagesize": 5
        }
        data = await fetch_with_retry(client, STACK_EXCHANGE_URL, params)
        
        items = data.get("items", [])
        normalized = []
        for item in items:
            normalized.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "description": f"Score: {item.get('score', 0)} | Answer Count: {item.get('answer_count', 0)}",
                "source": "Stack Overflow"
            })
        return normalized

    @staticmethod
    async def fetch_datasets(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        # Hugging Face Datasets API as a public fallback or Kaggle Dataset placeholder
        url = "https://huggingface.co/api/datasets"
        params = {"search": query, "limit": 5}
        try:
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                items = response.json()
                normalized = []
                for item in items:
                    normalized.append({
                        "title": item.get("id", ""),
                        "url": f"https://huggingface.co/datasets/{item.get('id', '')}",
                        "description": f"Downloads: {item.get('downloads', 0)} | Likes: {item.get('likes', 0)}",
                        "size": "N/A",
                        "creator": item.get("author", "HF")
                    })
                return normalized
        except Exception as e:
            logger.error(f"Hugging Face datasets fetch failed: {e}")
        
        # Fallback simulated dataset
        return [{
            "title": f"{query} dataset from Kaggle",
            "url": f"https://www.kaggle.com/search?q={query}",
            "description": f"A comprehensive public dataset for learning {query}.",
            "size": "15.4 MB",
            "creator": "Kaggle Community"
        }]

    @classmethod
    async def aggregate(cls, query: str) -> Dict[str, Any]:
        """
        Runs all API fetches concurrently using asyncio.gather.
        """
        async with httpx.AsyncClient() as client:
            tasks = [
                cls.fetch_github(client, query),
                cls.fetch_youtube(client, query),
                cls.fetch_google_books(client, query),
                cls.fetch_stack_exchange(client, query),
                cls.fetch_datasets(client, query)
            ]
            
            # Gather with return_exceptions=True so one failing service doesn't crash the whole search
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            repos = results[0] if not isinstance(results[0], Exception) else []
            videos = results[1] if not isinstance(results[1], Exception) else []
            books = results[2] if not isinstance(results[2], Exception) else []
            courses = results[3] if not isinstance(results[3], Exception) else []
            datasets = results[4] if not isinstance(results[4], Exception) else []
            
            # Simple static documentation links for key topics
            docs = []
            lower_q = query.lower()
            if "python" in lower_q:
                docs.append({"title": "Official Python Documentation", "url": "https://docs.python.org/3/"})
            elif "react" in lower_q:
                docs.append({"title": "Official React Documentation", "url": "https://react.dev/"})
            elif "fastapi" in lower_q:
                docs.append({"title": "Official FastAPI Documentation", "url": "https://fastapi.tiangolo.com/"})
            elif "postgres" in lower_q:
                docs.append({"title": "Official PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/"})
            else:
                docs.append({"title": f"Search docs for {query}", "url": f"https://devdocs.io/#q={query}"})

            return {
                "course": courses[0] if courses else None,
                "roadmap": [],
                "repositories": repos,
                "videos": videos,
                "books": books,
                "datasets": datasets,
                "documentation": docs
            }

import os
import httpx
import logging
import asyncio
from typing import List, Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/search/repositories"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
STACK_EXCHANGE_URL = "https://api.stackexchange.com/2.3/search/advanced"

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
                if "googleapis.com/books" in url and response.status_code in [403, 429]:
                    logger.warning("Google Books API quota exceeded or forbidden, breaking early.")
                    break
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
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
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
        if not settings.YOUTUBE_API_KEY:
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
            "key": settings.YOUTUBE_API_KEY
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
        data = await fetch_with_retry(client, GOOGLE_BOOKS_URL, params, retries=2, backoff=0.3)
        
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
        Runs all API fetches concurrently using asyncio.gather with dynamic queries.
        """
        from app.services.skill_config import normalize_skill, get_skill_category
        
        normalized_skill = normalize_skill(query)
        category = get_skill_category(normalized_skill)
        
        youtube_queries = []
        github_queries = []
        books_queries = []
        stack_queries = [normalized_skill]
        dataset_queries = [normalized_skill]

        if category == "Music":
            youtube_queries = [f"{normalized_skill} beginner lessons", f"{normalized_skill} tutorial", f"learn {normalized_skill}"]
            books_queries = [f"{normalized_skill} beginner", f"{normalized_skill} lessons", f"{normalized_skill} theory"]
            github_queries = [normalized_skill, "music practice", f"{normalized_skill} tools"]
        elif category == "Technology":
            youtube_queries = [f"{normalized_skill} beginner tutorial", f"learn {normalized_skill}", f"{normalized_skill} projects"]
            github_queries = [f"{normalized_skill} projects", f"{normalized_skill} beginner"]
            books_queries = [f"{normalized_skill} programming"]
        elif category == "Sports":
            if normalized_skill.lower() == "cricket":
                youtube_queries = ["cricket batting drills", "cricket bowling tutorial", "learn cricket"]
                books_queries = ["cricket coaching", "cricket fundamentals"]
            else:
                youtube_queries = [f"{normalized_skill} drills", f"{normalized_skill} tutorial", f"learn {normalized_skill}"]
                books_queries = [f"{normalized_skill} coaching", f"{normalized_skill} fundamentals"]
            github_queries = [normalized_skill]
        elif category == "Photography":
            youtube_queries = [f"{normalized_skill} tutorial", f"learn {normalized_skill}", f"{normalized_skill} for beginners"]
            books_queries = [f"{normalized_skill} fundamentals", f"{normalized_skill} guide"]
            github_queries = [normalized_skill]
        else:
            # Fallback for Dance, Art, Cooking, Languages, Communication, Other
            youtube_queries = [f"{normalized_skill} tutorial", f"learn {normalized_skill}", f"{normalized_skill} beginner lessons"]
            books_queries = [f"{normalized_skill} fundamentals", f"{normalized_skill} guide"]
            github_queries = [normalized_skill]

        async with httpx.AsyncClient() as client:
            # Gather tasks for all generated query variations
            github_tasks = [cls.fetch_github(client, q) for q in github_queries]
            youtube_tasks = [cls.fetch_youtube(client, q) for q in youtube_queries]
            books_tasks = [cls.fetch_google_books(client, q) for q in books_queries]
            stack_tasks = [cls.fetch_stack_exchange(client, q) for q in stack_queries]
            dataset_tasks = [cls.fetch_datasets(client, q) for q in dataset_queries]
            
            all_tasks = github_tasks + youtube_tasks + books_tasks + stack_tasks + dataset_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            # Unpack results in order
            idx = 0
            
            repos = []
            for _ in github_queries:
                res = results[idx]
                if not isinstance(res, Exception):
                    repos.extend(res)
                idx += 1
                
            videos = []
            for _ in youtube_queries:
                res = results[idx]
                if not isinstance(res, Exception):
                    videos.extend(res)
                idx += 1
                
            books = []
            for _ in books_queries:
                res = results[idx]
                if not isinstance(res, Exception):
                    books.extend(res)
                idx += 1
                
            courses = []
            for _ in stack_queries:
                res = results[idx]
                if not isinstance(res, Exception):
                    courses.extend(res)
                idx += 1
                
            datasets = []
            for _ in dataset_queries:
                res = results[idx]
                if not isinstance(res, Exception):
                    datasets.extend(res)
                idx += 1

            # Simple static documentation links for key topics
            docs = []
            lower_q = normalized_skill.lower()
            if "python" in lower_q:
                docs.append({"title": "Official Python Documentation", "url": "https://docs.python.org/3/"})
            elif "react" in lower_q:
                docs.append({"title": "Official React Documentation", "url": "https://react.dev/"})
            elif "fastapi" in lower_q:
                docs.append({"title": "Official FastAPI Documentation", "url": "https://fastapi.tiangolo.com/"})
            elif "postgres" in lower_q:
                docs.append({"title": "Official PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/"})
            else:
                docs.append({"title": f"Search docs for {normalized_skill}", "url": f"https://devdocs.io/#q={normalized_skill}"})

            return {
                "course": courses[0] if courses else None,
                "roadmap": [],
                "repositories": repos,
                "videos": videos,
                "books": books,
                "datasets": datasets,
                "documentation": docs
            }

    @classmethod
    async def aggregate_discover(cls, query: str) -> Dict[str, Any]:
        from app.services.skill_config import normalize_skill, get_skill_category
        
        normalized_skill = normalize_skill(query)
        category = get_skill_category(normalized_skill)
        
        youtube_queries = [f"learn {normalized_skill}", f"{normalized_skill} tutorial"]
        github_queries = [f"{normalized_skill} learning", f"{normalized_skill} examples"]
        books_queries = [f"{normalized_skill} beginner", f"{normalized_skill} guide"]
        
        interview_queries = []
        practice_queries = []
        project_queries = []
        course_queries = [f"{normalized_skill} course"]
        
        if category == "Technology":
            interview_queries = [f"{normalized_skill} interview questions"]
            practice_queries = [f"{normalized_skill} practice"]
            project_queries = [f"{normalized_skill} projects"]
            github_queries = [f"{normalized_skill} tutorials", f"{normalized_skill} roadmap"]
        elif category == "Music":
            youtube_queries = [f"{normalized_skill} beginner lessons"]
            github_queries = []
        
        async with httpx.AsyncClient() as client:
            github_tasks = [cls.fetch_github(client, q) for q in github_queries]
            youtube_tasks = [cls.fetch_youtube(client, q) for q in youtube_queries]
            books_tasks = [cls.fetch_google_books(client, q) for q in books_queries]
            
            interview_tasks = [cls.fetch_github(client, q) for q in interview_queries]
            practice_tasks = [cls.fetch_github(client, q) for q in practice_queries]
            project_tasks = [cls.fetch_github(client, q) for q in project_queries]
            course_tasks = [cls.fetch_youtube(client, q) for q in course_queries]
            
            all_tasks = github_tasks + youtube_tasks + books_tasks + interview_tasks + practice_tasks + project_tasks + course_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            idx = 0
            
            def extract(count):
                nonlocal idx
                res_list = []
                for _ in range(count):
                    res = results[idx]
                    if not isinstance(res, Exception):
                        res_list.extend(res)
                    idx += 1
                return res_list
                
            repos = extract(len(github_queries))
            videos = extract(len(youtube_queries))
            books = extract(len(books_queries))
            interview_questions = extract(len(interview_queries))
            practice = extract(len(practice_queries))
            projects = extract(len(project_queries))
            courses = extract(len(course_queries))
            
            docs = []
            lower_q = normalized_skill.lower()
            if "python" in lower_q:
                docs.append({"title": "Official Python Documentation", "url": "https://docs.python.org/3/"})
            elif "react" in lower_q:
                docs.append({"title": "Official React Documentation", "url": "https://react.dev/"})
            elif "fastapi" in lower_q:
                docs.append({"title": "Official FastAPI Documentation", "url": "https://fastapi.tiangolo.com/"})
            elif "postgres" in lower_q:
                docs.append({"title": "Official PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/"})
            elif category == "Technology":
                docs.append({"title": f"Search docs for {normalized_skill}", "url": f"https://devdocs.io/#q={normalized_skill}"})
            
            return {
                "videos": videos,
                "github": repos,
                "books": books,
                "interview_questions": interview_questions,
                "documentation": docs,
                "courses": courses,
                "practice": practice,
                "projects": projects
            }

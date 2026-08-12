import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.search_repository import search_repo
from app.services.aggregator import AggregatorService
from app.services.roadmap import roadmap_service
from app.services.skill_config import normalize_skill, get_skill_category
from typing import Dict, Any, Optional, List

class SearchService:
    """
    Service layer coordinates caching and aggregation logics.
    """

    @staticmethod
    def _to_dict(obj) -> Optional[Dict[str, Any]]:
        if obj is None:
            return None
        if hasattr(obj, "__dict__"):
            d = dict(obj.__dict__)
            d.pop("_sa_instance_state", None)
            return d
        elif isinstance(obj, dict):
            return dict(obj)
        return None

    @classmethod
    def rank_and_deduplicate(cls, resources: List[Any], skill: str, url_key: str = "url", title_key: str = "title") -> List[Dict[str, Any]]:
        seen_urls = set()
        seen_titles = set()
        unique_resources = []
        
        skill_lower = skill.lower()
        skill_words = set(skill_lower.split())
        
        for item_obj in resources:
            item = cls._to_dict(item_obj)
            url = item.get(url_key) or item.get("info_link") or ""
            title = item.get(title_key) or ""
            
            url_clean = url.strip().lower()
            title_clean = title.strip().lower()
            
            if not url_clean or not title_clean:
                continue
            if url_clean in seen_urls or title_clean in seen_titles:
                continue
                
            seen_urls.add(url_clean)
            seen_titles.add(title_clean)
            
            # Scoring
            score = 0
            desc = item.get("description") or ""
            desc_lower = desc.lower()
            
            if skill_lower in title_clean:
                score += 15
            elif any(w in title_clean for w in skill_words):
                score += 5
                
            if skill_lower in desc_lower:
                score += 8
                
            title_words = set(re.findall(r'\w+', title_clean))
            desc_words = set(re.findall(r'\w+', desc_lower))
            
            score += len(title_words.intersection(skill_words)) * 3
            score += len(desc_words.intersection(skill_words)) * 1
            
            if "stars" in item:
                try:
                    score += min(float(item["stars"]) / 1000.0, 5.0)
                except (ValueError, TypeError):
                    pass
                
            item["_score"] = score
            unique_resources.append(item)
            
        unique_resources.sort(key=lambda x: x.get("_score", 0), reverse=True)
        for item in unique_resources:
            item.pop("_score", None)
            
        return unique_resources

    @classmethod
    def map_resources_to_stages(cls, stages: List[Any], videos: List[Any], books: List[Any], repos: List[Any], datasets: List[Any], docs: List[Any], skill: str) -> List[Dict[str, Any]]:
        generic_words = {"fundamentals", "basics", "learn", "core", "understanding", "master", "the", "and", "of", "in", "for", "to", "with", "a", "an", skill.lower()}
        stage_words_list = []
        for stage in stages:
            title = getattr(stage, "step_title", "")
            desc = getattr(stage, "step_description", "") or ""
            w = set(re.findall(r'\w+', title.lower() + " " + desc.lower()))
            stage_words_list.append(w - generic_words)

        mapped_stages = []
        for idx, stage in enumerate(stages):
            title = getattr(stage, "step_title", "")
            desc = getattr(stage, "step_description", "") or ""
            stage_words = stage_words_list[idx]
            
            stage_videos = []
            stage_books = []
            stage_repos = []
            stage_datasets = []
            stage_docs = []
            
            def match_score(res_title: str, res_desc: str) -> float:
                score = 0.0
                res_text_words = set(re.findall(r'\w+', res_title.lower() + " " + (res_desc or "").lower()))
                overlap = stage_words.intersection(res_text_words)
                score += len(overlap) * 5.0
                for word in stage_words:
                    if len(word) > 3:
                        if word in res_title.lower():
                            score += 3.0
                        if word in (res_desc or "").lower():
                            score += 1.0
                return score

            # Match videos
            for v in videos:
                s = match_score(v.get("title", ""), v.get("description", ""))
                if s > 0:
                    stage_videos.append((s, v))
            stage_videos.sort(key=lambda x: x[0], reverse=True)

            # Match books
            for b in books:
                s = match_score(b.get("title", ""), b.get("description", ""))
                if s > 0:
                    stage_books.append((s, b))
            stage_books.sort(key=lambda x: x[0], reverse=True)

            # Match repos
            for r in repos:
                s = match_score(r.get("name", "") + " " + r.get("full_name", ""), r.get("description", ""))
                if s > 0:
                    stage_repos.append((s, r))
            stage_repos.sort(key=lambda x: x[0], reverse=True)

            # Match datasets
            for d in datasets:
                s = match_score(d.get("title", ""), d.get("description", ""))
                if s > 0:
                    stage_datasets.append((s, d))
            stage_datasets.sort(key=lambda x: x[0], reverse=True)

            # Match docs
            for dc in docs:
                s = match_score(dc.get("title", ""), dc.get("description", ""))
                if s > 0:
                    stage_docs.append((s, dc))
            stage_docs.sort(key=lambda x: x[0], reverse=True)

            mapped_stages.append({
                "step_title": title,
                "step_description": desc,
                "step_order": getattr(stage, "step_order", idx + 1),
                "resources": {
                    "videos": [item[1] for item in stage_videos[:2]],
                    "books": [item[1] for item in stage_books[:2]],
                    "repositories": [item[1] for item in stage_repos[:2]],
                    "datasets": [item[1] for item in stage_datasets[:2]],
                    "documentation": [item[1] for item in stage_docs[:2]]
                }
            })
        return mapped_stages

    @classmethod
    async def search_topic(cls, db: Session, query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        # Log to search history
        search_repo.log_search_history(db, query, user_id)

        normalized_skill = normalize_skill(query)
        clean_query = normalized_skill.lower().strip()
        category = get_skill_category(normalized_skill)

        metadata = search_repo.get_cache_metadata(db, clean_query)

        # Cache expiration threshold: 24 hours
        cache_valid = False
        if metadata:
            age = datetime.utcnow() - metadata.last_updated
            if age < timedelta(hours=24):
                cache_valid = True

        if cache_valid and metadata:
            # Hit cache
            raw_data = search_repo.get_cached_results(db, metadata)
        else:
            # Miss cache - fetch external APIs concurrently
            aggregated_data = await AggregatorService.aggregate(clean_query)
            
            # Save to cache
            saved_metadata = search_repo.save_cached_results(db, clean_query, aggregated_data)
            raw_data = search_repo.get_cached_results(db, saved_metadata)
            
        # Perform dynamic ranking & deduplication
        repos = cls.rank_and_deduplicate(raw_data.get("repositories", []), normalized_skill)
        videos = cls.rank_and_deduplicate(raw_data.get("videos", []), normalized_skill)
        books = cls.rank_and_deduplicate(raw_data.get("books", []), normalized_skill, url_key="info_link")
        datasets = cls.rank_and_deduplicate(raw_data.get("datasets", []), normalized_skill)
        docs = cls.rank_and_deduplicate(raw_data.get("documentation", []), normalized_skill)

        # Get or generate roadmap
        roadmap_stages = roadmap_service.get_roadmap(db, normalized_skill)
        mapped_roadmap = cls.map_resources_to_stages(roadmap_stages, videos, books, repos, datasets, docs, normalized_skill)

        return {
            "course": cls._to_dict(raw_data.get("course")) if raw_data.get("course") else None,
            "category": category,
            "roadmap": mapped_roadmap,
            "repositories": repos,
            "videos": videos,
            "books": books,
            "datasets": datasets,
            "documentation": docs,
            "last_updated": raw_data.get("last_updated", datetime.utcnow().isoformat())
        }

search_service = SearchService()


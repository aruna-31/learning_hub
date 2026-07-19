from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.category import Category
from app.models.roadmap_step import RoadmapStep
from app.models.user_progress import UserProgress
from app.schemas.analytics import AnalyticsResponse, CategoryProgressDistribution, AnalyticsCourseDetail
from collections import defaultdict

from app.models.search_history import SearchHistory
from app.schemas.trending import GlobalAnalyticsResponse, TrendingTopicSchema

class AnalyticsService:
    """
    Service class to aggregate complex analytics for the student.
    """

    def get_analytics_overview(self, db: Session, user_id: int) -> AnalyticsResponse:
        # Fetch enrollments with linked courses and categories
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()

        if not enrollments:
            return AnalyticsResponse()

        total_hours = 0
        overall_progress_sum = 0.0
        
        # Intermediate structures to calculate category distributions
        category_stats = defaultdict(lambda: {"count": 0, "progress_sum": 0.0})
        course_details_list = []

        for enroll in enrollments:
            course = enroll.course
            if not course:
                continue

            total_hours += course.duration_hours
            overall_progress_sum += enroll.progress_percent

            # Grouping by category
            category = course.category
            cat_name = category.name if category else "Uncategorized"
            category_stats[cat_name]["count"] += 1
            category_stats[cat_name]["progress_sum"] += enroll.progress_percent

            # Calculate step counts
            total_steps = db.query(RoadmapStep).filter(RoadmapStep.course_id == course.id).count()
            completed_steps = db.query(UserProgress).filter(UserProgress.enrollment_id == enroll.id).count()

            course_details_list.append(
                AnalyticsCourseDetail(
                    course_id=course.id,
                    course_title=course.title,
                    total_steps_count=total_steps,
                    completed_steps_count=completed_steps,
                    progress_percent=enroll.progress_percent,
                    duration_hours=course.duration_hours,
                    is_completed=enroll.progress_percent >= 100.0
                )
            )

        # Build category distribution objects
        cat_distributions = []
        for cat_name, stats in category_stats.items():
            count = stats["count"]
            average_progress_percent = stats["progress_sum"] / count if count > 0 else 0.0
            cat_distributions.append(
                CategoryProgressDistribution(
                    category_name=cat_name,
                    enrolled_courses_count=count,
                    average_progress_percent=average_progress_percent
                )
            )

        overall_avg = overall_progress_sum / len(enrollments) if enrollments else 0.0

        return AnalyticsResponse(
            total_study_hours_committed=total_hours,
            overall_average_progress=overall_avg,
            category_distribution=cat_distributions,
            course_details=course_details_list
        )

    def get_global_search_analytics(self, db: Session) -> GlobalAnalyticsResponse:
        """
        Returns global search history overview with trending topics.
        """
        from app.services.background_jobs import trending_topics_cache
        
        # If cache exists, use it
        if trending_topics_cache["last_updated"] is not None:
            return GlobalAnalyticsResponse(
                trending_topics=trending_topics_cache["topics"],
                total_searches=trending_topics_cache["total_searches"]
            )
            
        # Fallback to direct DB query
        trending_query = db.query(
            SearchHistory.query,
            func.count(SearchHistory.id).label("count"),
            func.max(SearchHistory.searched_at).label("last_searched")
        ).group_by(SearchHistory.query).order_by(func.count(SearchHistory.id).desc()).limit(10).all()

        trending_topics = []
        for row in trending_query:
            trending_topics.append(TrendingTopicSchema(
                query=row[0],
                count=row[1],
                last_searched_at=row[2]
            ))

        total_searches = db.query(SearchHistory).count()

        return GlobalAnalyticsResponse(
            trending_topics=trending_topics,
            total_searches=total_searches
        )

analytics_service = AnalyticsService()

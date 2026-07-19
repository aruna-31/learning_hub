from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment
from app.models.bookmark import Bookmark
from app.models.note import Note
from app.models.course import Course
from app.schemas.dashboard import DashboardMetricsResponse, ActiveCourseProgress

class DashboardService:
    """
    Service class to aggregate statistics for the student dashboard.
    """

    def get_dashboard_metrics(self, db: Session, user_id: int) -> DashboardMetricsResponse:
        # Get count metrics
        total_enrolled = db.query(Enrollment).filter(Enrollment.user_id == user_id).count()
        completed_count = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.progress_percent >= 100.0
        ).count()
        in_progress_count = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.progress_percent > 0.0,
            Enrollment.progress_percent < 100.0
        ).count()

        total_bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).count()
        total_notes = db.query(Note).filter(Note.user_id == user_id).count()

        # Fetch recent 5 enrollments with course details
        recent_enrollments = db.query(Enrollment).filter(
            Enrollment.user_id == user_id
        ).order_by(Enrollment.enrolled_at.desc()).limit(5).all()

        recent_courses_progress = []
        for enroll in recent_enrollments:
            recent_courses_progress.append(
                ActiveCourseProgress(
                    enrollment_id=enroll.id,
                    course_id=enroll.course_id,
                    course_title=enroll.course.title if enroll.course else "Unknown Course",
                    progress_percent=enroll.progress_percent,
                    enrolled_at=enroll.enrolled_at,
                    completed_at=enroll.completed_at
                )
            )

        return DashboardMetricsResponse(
            total_enrolled=total_enrolled,
            in_progress_count=in_progress_count,
            completed_count=completed_count,
            total_bookmarks=total_bookmarks,
            total_notes=total_notes,
            recent_courses=recent_courses_progress
        )

dashboard_service = DashboardService()

import sys
import os
# Adjust path to import app correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.user import User

client = TestClient(app)

def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test user if not exists
    test_user = db.query(User).filter(User.email == "dashboarduser@gmail.com").first()
    if not test_user:
        test_user = User(
            email="dashboarduser@gmail.com",
            full_name="Dashboard User",
            avatar="http://example.com/avatar.jpg"
        )
        db.add(test_user)
        db.commit()
    db.close()

def test_dashboard_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "dashboarduser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Dashboard Metrics
    metrics_response = client.get("/api/v1/dashboard/metrics", headers=headers)
    assert metrics_response.status_code == 200
    data = metrics_response.json()
    assert "total_enrolled" in data
    assert "in_progress_count" in data
    assert "completed_count" in data
    assert "total_bookmarks" in data
    assert "total_notes" in data

    # 3. Create dummy entities to verify updates
    # Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Dashboard Tech", "description": "Verification category"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Dashboard").json()["items"][0]["id"]

    # Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "Dashboard Design Masterclass",
            "description": "Building aggregate interfaces.",
            "instructor_name": "Dave Metrics",
            "difficulty_level": "Beginner",
            "duration_hours": 5,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=Dashboard").json()["items"][0]["id"]

    # Enroll in course
    enroll_response = client.post("/api/v1/enrollments", json={"course_id": course_id}, headers=headers)
    assert enroll_response.status_code in [201, 400]

    # Create Roadmap step
    step_response = client.post(
        "/api/v1/roadmap-steps",
        json={"title": "Introduction to Metrics", "step_order": 1, "course_id": course_id},
        headers=headers
    )
    assert step_response.status_code in [201, 400]
    step_id = client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"][0]["id"]

    # Create Resource
    res_response = client.post(
        "/api/v1/resources",
        json={"title": "Metric definitions", "url": "https://example.com/metrics", "type": "Other", "step_id": step_id},
        headers=headers
    )
    assert res_response.status_code in [201, 400]
    resource_id = client.get(f"/api/v1/resources?step_id={step_id}").json()["items"][0]["id"]

    # Bookmark resource
    client.post("/api/v1/bookmarks", json={"resource_id": resource_id}, headers=headers)

    # Add Note
    client.post("/api/v1/notes", json={"step_id": step_id, "content": "Dashboard notes"}, headers=headers)

    # 4. Fetch metrics again and verify updates
    updated_metrics_resp = client.get("/api/v1/dashboard/metrics", headers=headers)
    assert updated_metrics_resp.status_code == 200
    updated_data = updated_metrics_resp.json()
    
    # Assert values incremented
    assert updated_data["total_enrolled"] >= 1
    assert updated_data["total_bookmarks"] >= 1
    assert updated_data["total_notes"] >= 1
    assert len(updated_data["recent_courses"]) >= 1

    print("All tests in Dashboard Flow passed successfully!")

if __name__ == "__main__":
    test_dashboard_flow()

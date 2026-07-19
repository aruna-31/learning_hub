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
    test_user = db.query(User).filter(User.email == "analyticsuser@gmail.com").first()
    if not test_user:
        test_user = User(
            email="analyticsuser@gmail.com",
            full_name="Analytics User",
            avatar="http://example.com/avatar.jpg"
        )
        db.add(test_user)
        db.commit()
    db.close()

def test_analytics_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "analyticsuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Analytics Overview
    overview_response = client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_response.status_code == 200
    data = overview_response.json()
    assert "total_study_hours_committed" in data
    assert "overall_average_progress" in data
    assert "category_distribution" in data
    assert "course_details" in data

    # 3. Create dummy entities to verify updates
    # Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Analytics Tech", "description": "Verification category"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Analytics").json()["items"][0]["id"]

    # Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "Analytics System Design",
            "description": "Building aggregators.",
            "instructor_name": "Dr. Analytics",
            "difficulty_level": "Intermediate",
            "duration_hours": 10,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=Analytics").json()["items"][0]["id"]

    # Enroll in course
    enroll_response = client.post("/api/v1/enrollments", json={"course_id": course_id}, headers=headers)
    assert enroll_response.status_code in [201, 400]

    # Get updated metrics
    updated_resp = client.get("/api/v1/analytics/overview", headers=headers)
    assert updated_resp.status_code == 200
    updated_data = updated_resp.json()
    
    # Assert values incremented
    assert updated_data["total_study_hours_committed"] >= 10
    assert len(updated_data["category_distribution"]) >= 1
    assert len(updated_data["course_details"]) >= 1

    print("All tests in Analytics Flow passed successfully!")

def test_global_analytics_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "analyticsuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Trigger search query logs via /search
    for _ in range(10):
        client.get("/api/v1/search?query=Python", headers=headers)
    client.get("/api/v1/search?query=React", headers=headers)

    # 3. Retrieve global search analytics
    global_response = client.get("/api/v1/analytics", headers=headers)
    assert global_response.status_code == 200
    data = global_response.json()
    assert "total_searches" in data
    assert "trending_topics" in data
    assert data["total_searches"] >= 11
    
    # Verify Python is first trending (since it was searched 10 times)
    trending = data["trending_topics"]
    assert len(trending) >= 2
    assert trending[0]["query"].lower() == "python"
    assert trending[0]["count"] >= 10

if __name__ == "__main__":
    test_analytics_flow()
    test_global_analytics_flow()

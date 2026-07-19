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
    test_user = db.query(User).filter(User.email == "testuser@gmail.com").first()
    if not test_user:
        test_user = User(
            email="testuser@gmail.com",
            full_name="Test User",
            avatar="http://example.com/avatar.jpg"
        )
        db.add(test_user)
        db.commit()
    db.close()

def test_progress_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Software Architecture", "description": "System Design courses"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Architecture").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "Clean Code and Design Patterns",
            "description": "Solid principles and clean architecture concepts.",
            "instructor_name": "Uncle Bob",
            "difficulty_level": "Advanced",
            "duration_hours": 20,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=Clean").json()["items"][0]["id"]

    # 4. Create 2 Roadmap Steps
    step1_response = client.post(
        "/api/v1/roadmap-steps",
        json={"title": "SOLID Principles", "step_order": 1, "course_id": course_id},
        headers=headers
    )
    assert step1_response.status_code in [201, 400]

    step2_response = client.post(
        "/api/v1/roadmap-steps",
        json={"title": "Design Patterns", "step_order": 2, "course_id": course_id},
        headers=headers
    )
    assert step2_response.status_code in [201, 400]

    steps = client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"]
    step1_id = steps[0]["id"]
    step2_id = steps[1]["id"]

    # 5. Enroll in Course
    enroll_response = client.post("/api/v1/enrollments", json={"course_id": course_id}, headers=headers)
    assert enroll_response.status_code in [201, 400]
    
    enrollments_data = client.get(f"/api/v1/enrollments?course_id={course_id}", headers=headers).json()
    enrollment_id = enrollments_data["items"][0]["id"]

    # 6. Complete step 1 -> Verify progress is 50%
    toggle1_response = client.post(
        "/api/v1/progress",
        json={"enrollment_id": enrollment_id, "step_id": step1_id, "completed": True},
        headers=headers
    )
    assert toggle1_response.status_code == 200
    
    status_response = client.get(f"/api/v1/progress/status/{enrollment_id}", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["progress_percent"] == 50.0
    assert status_response.json()["is_completed"] is False
    assert status_response.json()["completed_at"] is None

    # 7. Complete step 2 -> Verify progress is 100%, completed_at is populated
    toggle2_response = client.post(
        "/api/v1/progress",
        json={"enrollment_id": enrollment_id, "step_id": step2_id, "completed": True},
        headers=headers
    )
    assert toggle2_response.status_code == 200

    status_response2 = client.get(f"/api/v1/progress/status/{enrollment_id}", headers=headers)
    assert status_response2.status_code == 200
    assert status_response2.json()["progress_percent"] == 100.0
    assert status_response2.json()["is_completed"] is True
    assert status_response2.json()["completed_at"] is not None

    # 8. Mark step 2 incomplete -> Verify progress is 50%, completed_at is cleared
    toggle2_false_response = client.post(
        "/api/v1/progress",
        json={"enrollment_id": enrollment_id, "step_id": step2_id, "completed": False},
        headers=headers
    )
    assert toggle2_false_response.status_code == 200

    status_response3 = client.get(f"/api/v1/progress/status/{enrollment_id}", headers=headers)
    assert status_response3.status_code == 200
    assert status_response3.json()["progress_percent"] == 50.0
    assert status_response3.json()["is_completed"] is False
    assert status_response3.json()["completed_at"] is None

    print("All tests in Progress Flow passed successfully!")

if __name__ == "__main__":
    test_progress_flow()

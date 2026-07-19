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

def test_roadmap_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "DevOps Tools", "description": "Cloud and DevOps categories"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    if cat_response.status_code == 201:
        category_id = cat_response.json()["id"]
    else:
        category_id = client.get("/api/v1/categories?search=DevOps").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "Docker Containerization Guide",
            "description": "Comprehensive guide to Docker and containers",
            "instructor_name": "Jane DevOps",
            "difficulty_level": "Beginner",
            "duration_hours": 10,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    if course_response.status_code == 201:
        course_id = course_response.json()["id"]
    else:
        course_id = client.get("/api/v1/courses?search=Docker").json()["items"][0]["id"]

    # 4. Create Roadmap Steps
    step1_payload = {
        "title": "Introduction to Containers",
        "description": "Understanding what containers are and why we use them.",
        "step_order": 1,
        "course_id": course_id
    }
    step1_response = client.post("/api/v1/roadmap-steps", json=step1_payload, headers=headers)
    assert step1_response.status_code in [201, 400], f"Failed to create step 1: {step1_response.text}"
    
    # 5. Attempt duplicate step_order = 1 (should fail with HTTP 400)
    duplicate_payload = {
        "title": "Docker Setup",
        "description": "Installing docker on local system.",
        "step_order": 1, # duplicate!
        "course_id": course_id
    }
    dup_response = client.post("/api/v1/roadmap-steps", json=duplicate_payload, headers=headers)
    assert dup_response.status_code == 400, f"Should have failed duplicate order check: {dup_response.text}"

    # 6. Create step 2 successfully
    step2_payload = {
        "title": "Installing Docker Engine",
        "description": "Installation guide for Mac/Windows/Linux.",
        "step_order": 2,
        "course_id": course_id
    }
    step2_response = client.post("/api/v1/roadmap-steps", json=step2_payload, headers=headers)
    assert step2_response.status_code == 201

    step1_id = step1_response.json()["id"] if step1_response.status_code == 201 else client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"][0]["id"]

    # 7. Update step 1 details
    update_payload = {
        "description": "Deep understanding of container concepts and virtual machines comparison."
    }
    update_response = client.put(f"/api/v1/roadmap-steps/{step1_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert "virtual machines comparison" in update_response.json()["description"]

    # 8. Course deletion should cascade delete steps
    delete_course_resp = client.delete(f"/api/v1/courses/{course_id}", headers=headers)
    assert delete_course_resp.status_code == 204

    # Verify steps are gone
    get_steps = client.get(f"/api/v1/roadmap-steps?course_id={course_id}")
    assert get_steps.status_code == 200
    assert len(get_steps.json()["items"]) == 0

    print("All tests in Roadmap Step Flow passed successfully!")

if __name__ == "__main__":
    test_roadmap_flow()

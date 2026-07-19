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

def test_enrollment_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Cloud Computing", "description": "AWS, GCP, Azure courses"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Cloud").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "AWS Certified Solutions Architect",
            "description": "Prepare for the AWS SAA-C03 exam.",
            "instructor_name": "Stephane Cloud",
            "difficulty_level": "Intermediate",
            "duration_hours": 27,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=AWS").json()["items"][0]["id"]

    # 4. Enroll Student
    enroll_payload = {"course_id": course_id}
    enroll_response = client.post("/api/v1/enrollments", json=enroll_payload, headers=headers)
    assert enroll_response.status_code in [201, 400], f"Enroll failed: {enroll_response.text}"

    # 5. Attempt duplicate enrollment (should fail with HTTP 400)
    dup_response = client.post("/api/v1/enrollments", json=enroll_payload, headers=headers)
    assert dup_response.status_code == 400, f"Should have failed duplicate enrollment: {dup_response.text}"

    # 6. List Enrollments
    list_response = client.get(f"/api/v1/enrollments?course_id={course_id}", headers=headers)
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["items"]) >= 1
    enrollment_id = list_data["items"][0]["id"]

    # 7. Get specific enrollment
    single_response = client.get(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
    assert single_response.status_code == 200
    assert single_response.json()["course_id"] == course_id

    # 8. Unenroll (delete enrollment)
    delete_response = client.delete(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify not found
    get_again = client.get(f"/api/v1/enrollments/{enrollment_id}", headers=headers)
    assert get_again.status_code == 404

    print("All tests in Enrollment Flow passed successfully!")

if __name__ == "__main__":
    test_enrollment_flow()

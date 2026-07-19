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

def test_course_flow():
    setup_test_db()
    
    # 1. Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category to link course to
    cat_payload = {
        "name": "Programming Languages",
        "description": "Courses about popular programming languages"
    }
    cat_response = client.post("/api/v1/categories", json=cat_payload, headers=headers)
    assert cat_response.status_code in [201, 400]
    
    if cat_response.status_code == 201:
        category_id = cat_response.json()["id"]
    else:
        # Retrieve existing
        get_cats = client.get("/api/v1/categories?search=Programming")
        assert get_cats.status_code == 200
        category_id = get_cats.json()["items"][0]["id"]

    # 3. Create Course
    course_payload = {
        "title": "Python Programming Masterclass",
        "description": "Learn Python programming from scratch to advanced concepts",
        "instructor_name": "Dr. John Doe",
        "difficulty_level": "Beginner",
        "duration_hours": 32,
        "category_id": category_id
    }
    course_response = client.post("/api/v1/courses", json=course_payload, headers=headers)
    assert course_response.status_code in [201, 400], f"Course creation failed: {course_response.text}"
    
    # 4. Try creating course with invalid difficulty level (should fail validation)
    bad_payload = course_payload.copy()
    bad_payload["title"] = "Python Advanced Course"
    bad_payload["difficulty_level"] = "Expert"  # Invalid!
    bad_response = client.post("/api/v1/courses", json=bad_payload, headers=headers)
    assert bad_response.status_code == 422, f"Should have failed validation: {bad_response.text}"

    # 5. List and Search Courses
    list_response = client.get(f"/api/v1/courses?search=Python&category_id={category_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["items"]) >= 1
    
    course_id = list_data["items"][0]["id"]

    # 6. Retrieve Single Course details
    single_response = client.get(f"/api/v1/courses/{course_id}")
    assert single_response.status_code == 200
    assert single_response.json()["title"] == "Python Programming Masterclass"

    # 7. Update Course
    update_payload = {
        "difficulty_level": "Intermediate",
        "duration_hours": 40
    }
    update_response = client.put(f"/api/v1/courses/{course_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["difficulty_level"] == "Intermediate"
    assert update_response.json()["duration_hours"] == 40

    # 8. Delete Course
    delete_response = client.delete(f"/api/v1/courses/{course_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify not found
    get_again = client.get(f"/api/v1/courses/{course_id}")
    assert get_again.status_code == 404

    print("All tests in Course Flow passed successfully!")

if __name__ == "__main__":
    test_course_flow()

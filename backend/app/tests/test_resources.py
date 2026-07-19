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

def test_resource_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Frontend Basics", "description": "HTML, CSS, JS courses"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Frontend").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "React JS for Beginners",
            "description": "Learn React JS hooks and state management",
            "instructor_name": "John React",
            "difficulty_level": "Beginner",
            "duration_hours": 15,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=React").json()["items"][0]["id"]

    # 4. Create Roadmap Step
    step_response = client.post(
        "/api/v1/roadmap-steps",
        json={
            "title": "Understanding JSX",
            "description": "How JSX renders HTML in React",
            "step_order": 1,
            "course_id": course_id
        },
        headers=headers
    )
    assert step_response.status_code in [201, 400]
    step_id = client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"][0]["id"]

    # 5. Create Resource
    resource_payload = {
        "title": "Official React JSX Docs",
        "url": "https://react.dev/learn/writing-markup-with-jsx",
        "type": "Document",
        "step_id": step_id
    }
    res_response = client.post("/api/v1/resources", json=resource_payload, headers=headers)
    assert res_response.status_code in [201, 400], f"Failed to create resource: {res_response.text}"
    
    # 6. Attempt creating with invalid URL format (should fail with HTTP 422)
    bad_url_payload = resource_payload.copy()
    bad_url_payload["url"] = "invalid_url_format"
    bad_url_payload["title"] = "Bad Resource"
    bad_url_response = client.post("/api/v1/resources", json=bad_url_payload, headers=headers)
    assert bad_url_response.status_code == 422, f"Should have failed URL validation: {bad_url_response.text}"

    # 7. Attempt creating with invalid type (should fail with HTTP 422)
    bad_type_payload = resource_payload.copy()
    bad_type_payload["type"] = "InvalidType"
    bad_type_payload["title"] = "Bad Resource 2"
    bad_type_response = client.post("/api/v1/resources", json=bad_type_payload, headers=headers)
    assert bad_type_response.status_code == 422, f"Should have failed type validation: {bad_type_response.text}"

    # 8. List and Search Resources
    list_response = client.get(f"/api/v1/resources?step_id={step_id}&type=Document")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["items"]) >= 1
    
    resource_id = list_data["items"][0]["id"]

    # 9. Get Single Resource
    single_response = client.get(f"/api/v1/resources/{resource_id}")
    assert single_response.status_code == 200
    assert single_response.json()["title"] == "Official React JSX Docs"

    # 10. Update Resource
    update_payload = {
        "type": "Article",
        "title": "Updated React JSX Docs"
    }
    update_response = client.put(f"/api/v1/resources/{resource_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["type"] == "Article"
    assert update_response.json()["title"] == "Updated React JSX Docs"

    # 11. Delete Roadmap Step should cascade delete the resource
    del_step_response = client.delete(f"/api/v1/roadmap-steps/{step_id}", headers=headers)
    assert del_step_response.status_code == 204

    # Verify resource is gone
    get_res_again = client.get(f"/api/v1/resources/{resource_id}")
    assert get_res_again.status_code == 404

    print("All tests in Resource Flow passed successfully!")

if __name__ == "__main__":
    test_resource_flow()

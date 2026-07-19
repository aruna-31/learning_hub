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

def test_bookmark_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Database Management", "description": "SQL and NoSQL databases"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Database").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "PostgreSQL Advanced Guide",
            "description": "Index design, query optimization, and replica configuration.",
            "instructor_name": "Craig Postgres",
            "difficulty_level": "Advanced",
            "duration_hours": 18,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=PostgreSQL").json()["items"][0]["id"]

    # 4. Create Roadmap Step
    step_response = client.post(
        "/api/v1/roadmap-steps",
        json={"title": "Indexes in PostgreSQL", "step_order": 1, "course_id": course_id},
        headers=headers
    )
    assert step_response.status_code in [201, 400]
    step_id = client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"][0]["id"]

    # 5. Create Resource
    resource_payload = {
        "title": "PostgreSQL Indexing docs",
        "url": "https://www.postgresql.org/docs/current/indexes.html",
        "type": "Document",
        "step_id": step_id
    }
    res_response = client.post("/api/v1/resources", json=resource_payload, headers=headers)
    assert res_response.status_code in [201, 400]
    resource_id = client.get(f"/api/v1/resources?step_id={step_id}").json()["items"][0]["id"]

    # 6. Bookmark Resource
    bookmark_response = client.post("/api/v1/bookmarks", json={"resource_id": resource_id}, headers=headers)
    assert bookmark_response.status_code in [201, 400], f"Bookmark failed: {bookmark_response.text}"

    # 7. Attempt duplicate bookmark (should fail with HTTP 400)
    dup_response = client.post("/api/v1/bookmarks", json={"resource_id": resource_id}, headers=headers)
    assert dup_response.status_code == 400, f"Should have failed duplicate bookmark: {dup_response.text}"

    # 8. List Bookmarks
    list_response = client.get("/api/v1/bookmarks", headers=headers)
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["items"]) >= 1
    bookmark_id = list_data["items"][0]["id"]

    # Verify resource details were included in bookmark list items
    assert list_data["items"][0]["resource"]["title"] == "PostgreSQL Indexing docs"

    # 9. Remove Bookmark
    delete_response = client.delete(f"/api/v1/bookmarks/{bookmark_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify not found
    get_again = client.get("/api/v1/bookmarks", headers=headers)
    assert get_again.status_code == 200
    assert len(get_again.json()["items"]) == 0

    print("All tests in Bookmark Flow passed successfully!")

if __name__ == "__main__":
    test_bookmark_flow()

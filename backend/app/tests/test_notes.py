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

def test_note_flow():
    setup_test_db()
    
    # 1. Login
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Category
    cat_response = client.post(
        "/api/v1/categories",
        json={"name": "Software Testing", "description": "QA and Automation courses"},
        headers=headers
    )
    assert cat_response.status_code in [201, 400]
    category_id = client.get("/api/v1/categories?search=Testing").json()["items"][0]["id"]

    # 3. Create Course
    course_response = client.post(
        "/api/v1/courses",
        json={
            "title": "Selenium with Python Guide",
            "description": "Learn test automation with Selenium Webdriver.",
            "instructor_name": "Dave Selenium",
            "difficulty_level": "Intermediate",
            "duration_hours": 12,
            "category_id": category_id
        },
        headers=headers
    )
    assert course_response.status_code in [201, 400]
    course_id = client.get("/api/v1/courses?search=Selenium").json()["items"][0]["id"]

    # 4. Create Roadmap Step
    step_response = client.post(
        "/api/v1/roadmap-steps",
        json={"title": "Webdriver Locators", "step_order": 1, "course_id": course_id},
        headers=headers
    )
    assert step_response.status_code in [201, 400]
    step_id = client.get(f"/api/v1/roadmap-steps?course_id={course_id}").json()["items"][0]["id"]

    # 5. Create Note
    note_payload = {
        "step_id": step_id,
        "content": "# Webdriver Locators Notes\n- ID locator is the fastest.\n- XPath is slower but flexible."
    }
    note_response = client.post("/api/v1/notes", json=note_payload, headers=headers)
    assert note_response.status_code in [201, 400], f"Note creation failed: {note_response.text}"

    # 6. Attempt duplicate note creation (should fail with HTTP 400)
    dup_response = client.post("/api/v1/notes", json=note_payload, headers=headers)
    assert dup_response.status_code == 400, f"Should have failed duplicate note: {dup_response.text}"

    # 7. List Notes
    list_response = client.get(f"/api/v1/notes?step_id={step_id}", headers=headers)
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data["items"]) >= 1
    note_id = list_data["items"][0]["id"]

    # 8. Update Note
    update_payload = {
        "content": "# Webdriver Locators Notes\n- ID locator is the fastest.\n- CSS Selector is preferred over XPath."
    }
    update_response = client.put(f"/api/v1/notes/{note_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert "CSS Selector is preferred" in update_response.json()["content"]

    # 9. Get Single Note details
    single_response = client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert single_response.status_code == 200
    assert single_response.json()["content"] == update_response.json()["content"]

    # 10. Delete Note
    delete_response = client.delete(f"/api/v1/notes/{note_id}", headers=headers)
    assert delete_response.status_code == 204

    # Verify not found
    get_again = client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get_again.status_code == 404

    print("All tests in Note Flow passed successfully!")

if __name__ == "__main__":
    test_note_flow()

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
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create a test user for auth if not exists
    test_user = db.query(User).filter(User.email == "testuser@gmail.com").first()
    if not test_user:
        test_user = User(
            email="testuser@gmail.com",
            full_name="Test User",
            avatar="http://example.com/avatar.jpg"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    db.close()

def test_category_flow():
    setup_test_db()
    
    # 1. Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Category
    payload = {
        "name": "Software Engineering",
        "description": "Roadmaps and resources for software engineers"
    }
    response = client.post("/api/v1/categories", json=payload, headers=headers)
    # Could be 201 Created or 400 if it already exists from a previous run
    assert response.status_code in [201, 400], f"Create Category failed: {response.text}"
    
    # 3. Get all Categories (public endpoint)
    get_response = client.get("/api/v1/categories")
    assert get_response.status_code == 200
    data = get_response.json()
    assert "items" in data
    assert "total" in data
    
    # 4. Search categories
    search_response = client.get("/api/v1/categories?search=Software")
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data["items"]) >= 1
    
    # Retrieve the created or existing category details
    category = search_data["items"][0]
    cat_id = category["id"]
    
    # 5. Get Single Category
    single_response = client.get(f"/api/v1/categories/{cat_id}")
    assert single_response.status_code == 200
    assert single_response.json()["name"] == category["name"]
    
    # 6. Update Category
    update_payload = {
        "description": "Updated description for Software Engineering"
    }
    update_response = client.put(f"/api/v1/categories/{cat_id}", json=update_payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated description for Software Engineering"
    
    # 7. Delete Category
    delete_response = client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    assert delete_response.status_code == 204
    
    print("All tests in Category Flow passed successfully!")

if __name__ == "__main__":
    test_category_flow()

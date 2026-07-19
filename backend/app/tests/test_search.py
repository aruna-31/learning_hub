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

def test_search_endpoint():
    setup_test_db()
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Search for a topic (should miss cache and trigger external aggregator fetch)
    response = client.get("/api/v1/search?query=FastAPI", headers=headers)
    assert response.status_code == 200, f"Search failed: {response.text}"
    
    data = response.json()
    assert "course" in data
    assert "repositories" in data
    assert "videos" in data
    assert "books" in data
    assert "datasets" in data
    assert "documentation" in data
    assert "last_updated" in data
    
    # 2. Search again (should hit cache immediately)
    cache_hit_response = client.get("/api/v1/search?query=FastAPI", headers=headers)
    assert cache_hit_response.status_code == 200
    cache_hit_data = cache_hit_response.json()
    assert cache_hit_data["last_updated"] == data["last_updated"]

if __name__ == "__main__":
    test_search_endpoint()

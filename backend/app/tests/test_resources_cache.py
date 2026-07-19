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

def test_resources_cache_endpoints():
    setup_test_db()
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch videos
    response = client.get("/api/v1/videos/fastapi", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # 2. Fetch repositories
    response = client.get("/api/v1/repositories/fastapi", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # 3. Fetch books
    response = client.get("/api/v1/books/fastapi", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # 4. Fetch datasets
    response = client.get("/api/v1/datasets/fastapi", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # 5. Fetch documentation
    response = client.get("/api/v1/documentation/fastapi", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

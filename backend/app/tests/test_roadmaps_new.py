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

def test_roadmap_flow():
    setup_test_db()
    
    # Login to get token
    login_response = client.post("/api/v1/auth/login", json={"email": "testuser@gmail.com"})
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch roadmap (should import and save to DB)
    response = client.get("/api/v1/roadmap/fastapi", headers=headers)
    assert response.status_code == 200, f"Roadmap failed: {response.text}"
    steps = response.json()
    assert len(steps) > 0
    assert steps[0]["step_title"] == "FastAPI Basics"
    assert steps[0]["step_order"] == 1
    
    # 2. Fetch again (should hit DB immediately)
    response2 = client.get("/api/v1/roadmap/fastapi", headers=headers)
    assert response2.status_code == 200
    steps2 = response2.json()
    assert len(steps2) == len(steps)
    
    # 3. Try to fetch invalid roadmap
    response_invalid = client.get("/api/v1/roadmap/invalidtopic", headers=headers)
    assert response_invalid.status_code == 404

if __name__ == "__main__":
    test_roadmap_flow()

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import app_settings

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == f"Welcome to {app_settings.app_name}!"

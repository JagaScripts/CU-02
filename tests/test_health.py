import pytest
from fastapi.testclient import TestClient
from cu02_app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_monitoring_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "is_running" in response.json()

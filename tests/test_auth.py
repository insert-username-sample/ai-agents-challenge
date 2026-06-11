import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_auth_token_success():
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "advocate", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_auth_token_incorrect_password():
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "advocate", "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert "Incorrect username or password" in response.json()["detail"]

def test_secured_endpoint_without_token():
    response = client.get("/api/v1/stats")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_secured_endpoint_invalid_token():
    response = client.get(
        "/api/v1/stats",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_secured_endpoint_success():
    # 1. Get token
    token_response = client.post(
        "/api/v1/auth/token",
        data={"username": "senior_partner", "password": "password123"},
    )
    token = token_response.json()["access_token"]
    
    # 2. Access stats
    response = client.get(
        "/api/v1/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    # Expect stats keys
    assert "total_signals" in data
    assert "average_reward" in data

from fastapi.testclient import TestClient
from api.main import app
from services.cryptography_service import CryptographyService

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Operations API", "version": "1.0.0"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_determinism_with_different_key_order():
    data1 = {"name": "Fulcrum", "version": 1, "status": "active"}
    data2 = {"version": 1, "status": "active", "name": "Fulcrum"}

    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)

    assert hash1 is not None
    assert hash1 == hash2

def test_null_values_are_ignored():
    data1 = {"name": "Fulcrum", "version": 1, "notes": None}
    data2 = {"version": 1, "name": "Fulcrum"}

    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)

    assert hash1 == hash2

def test_nested_object_determinism():
    data1 = {
        "event": "AIC_STATUS_CHANGE",
        "details": {"new_status": "AIC-1", "reason": "Efficiency drop"},
        "agent_id": "agent-123",
    }
    data2 = {
        "agent_id": "agent-123",
        "event": "AIC_STATUS_CHANGE",
        "details": {"reason": "Efficiency drop", "new_status": "AIC-1"},
    }

    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)

    assert hash1 is not None
    assert hash1 == hash2

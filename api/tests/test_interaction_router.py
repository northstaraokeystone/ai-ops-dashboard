# This is our single, unified test file.

# Imports for API testing
from starlette.testclient import TestClient

# Imports for business logic testing
from api.services.cryptography_service import CryptographyService


# We pass the 'client' fixture (from conftest.py) to all API tests
def test_health(client: TestClient):
    """Tests the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "healthy"
    assert response_data["secrets_loaded"] is True


def test_root(client: TestClient):
    """Tests the root / endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Operations API", "version": "1.0.0"}


def test_create_and_verify_idempotency(client: TestClient, valid_payload: dict):
    """
    Tests the interaction creation endpoint and its idempotency.
    """
    # Part 1: First submission should create a new resource.
    first_response = client.post("/api/interaction/", json=valid_payload)
    assert first_response.status_code == 201, (
        f"First submission failed: {first_response.text}"
    )

    first_data = first_response.json()
    assert "id" in first_data
    assert first_data["payload_hash"] is not None

    assert "agent_support" in first_data
    assert first_data["agent_support"]["message"] == "Final test successful."

    # Part 2: Second submission with the same payload should return the existing resource.
    second_response = client.post("/api/interaction/", json=valid_payload)
    assert second_response.status_code == 200, (
        "Idempotency check failed: expected 200 on second post"
    )

    second_data = second_response.json()
    assert first_data["id"] == second_data["id"]


# --- Cryptography Service Unit Tests ---
# These do not need the 'client' fixture as they test pure Python logic.


def test_determinism_with_different_key_order():
    """Tests that hash is the same regardless of key order."""
    data1 = {"name": "Fulcrum", "version": 1}
    data2 = {"version": 1, "name": "Fulcrum"}
    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)
    assert hash1 is not None
    assert hash1 == hash2


def test_null_values_are_ignored():
    """Tests that null values are excluded from the hash."""
    data1 = {"name": "Fulcrum", "version": 1, "notes": None}
    data2 = {"version": 1, "name": "Fulcrum"}
    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)
    assert hash1 == hash2


def test_nested_object_determinism():
    """Tests that hashing works correctly on nested objects."""
    data1 = {"event": "test", "details": {"status": "ok", "code": 1}}
    data2 = {"event": "test", "details": {"code": 1, "status": "ok"}}
    hash1 = CryptographyService.generate_hash(data1)
    hash2 = CryptographyService.generate_hash(data2)
    assert hash1 is not None
    assert hash1 == hash2

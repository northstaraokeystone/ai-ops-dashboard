import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture to provide a FastAPI TestClient for integration testing."""
    return TestClient(app)


@pytest.fixture(scope="module")
def valid_payload() -> dict:
    """Fixture to provide a consistent valid payload for testing."""
    return {
        "agent_id": str(uuid4()),
        "environment_hash": "test_environment_hash_sequential",
        "causality_id": str(uuid4()),
        "action_type": 1,
        "payload": {"key": "value_sequential", "nested": {"subkey": 42}},
    }


def test_create_and_verify_idempotency(client: TestClient, valid_payload: dict) -> None:
    """
    A single, sequential test for creating and then verifying an interaction.
    This avoids test state pollution by controlling the order of operations.
    """
    # --- Part 1: First submission (should create new) ---
    first_response = client.post("/interactions/", json=valid_payload)
    assert (
        first_response.status_code == 201
    ), f"First submission expected 201, got {first_response.status_code}"

    first_data = first_response.json()
    assert (
        first_data["status"] == "LOGGED"
    ), f"First status expected 'LOGGED', got {first_data.get('status')}"

    try:
        first_id = UUID(first_data["id"])
    except (ValueError, KeyError):
        pytest.fail(f"Invalid or missing UUID for first 'id': {first_data.get('id')}")

    # --- Part 2: Second submission (same payload, should detect duplicate) ---
    second_response = client.post("/interactions/", json=valid_payload)
    assert (
        second_response.status_code == 200
    ), f"Second submission expected 200, got {second_response.status_code}"

    second_data = second_response.json()
    assert (
        second_data["status"] == "DUPLICATE"
    ), f"Second status expected 'DUPLICATE', got {second_data.get('status')}"

    try:
        second_id = UUID(second_data["id"])
    except (ValueError, KeyError):
        pytest.fail(f"Invalid or missing UUID for second 'id': {second_data.get('id')}")

    # --- Part 3: Verify the ID matches the first submission ---
    assert (
        first_id == second_id
    ), f"IDs do not match: first {first_id}, second {second_id}"

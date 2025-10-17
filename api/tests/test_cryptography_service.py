from fastapi.testclient import TestClient
from api.main import app

# This client fixture is shared across tests in this file
client = TestClient(app)


def test_health():
    """Tests if the health check endpoint is working correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    # UPDATED: Assert the full, correct response from the health endpoint
    assert response.json() == {"status": "healthy", "secrets_loaded": True}


# NOTE: The rest of your cryptography tests would go here.
# For now, we're just ensuring the health check is correct.

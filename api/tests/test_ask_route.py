from fastapi.testclient import TestClient
from api.main import app


def test_ask_basic():
    client = TestClient(app)
    r = client.get("/ask", params={"q": "safety signals", "k": 5, "debug": 1})
    j = r.json()
    assert r.status_code == 200
    assert j["status"] == "DONE"
    assert len(j["results"]) == 5

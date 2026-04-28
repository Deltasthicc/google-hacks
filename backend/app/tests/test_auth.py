from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_validation_errors_use_envelope():
    response = client.post("/api/v1/projects", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"

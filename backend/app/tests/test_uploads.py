from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_project_and_upload_dataset():
    project_response = client.post("/api/v1/projects", json={"name": "Demo"})
    assert project_response.status_code == 200
    project_body = project_response.json()
    assert project_body["success"] is True
    project_id = project_body["data"]["project_id"]
    assert project_id.startswith("project_")

    upload_response = client.post(
        "/api/v1/upload-dataset",
        data={"project_id": project_id},
        files={"file": ("demo.csv", b"target,gender\n1,F\n", "text/csv")},
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert upload_body["success"] is True
    assert upload_body["data"]["upload_id"].startswith("upload_")
    assert "storage_path" not in upload_body["data"]

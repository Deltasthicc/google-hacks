from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_audit_and_report_flow():
    project_id = client.post("/api/v1/projects", json={"name": "Demo"}).json()["data"][
        "project_id"
    ]
    audit_response = client.post(
        "/api/v1/run-data-audit",
        json={
            "project_id": project_id,
            "upload_id": "upload_demo",
            "target_column": "approved",
            "sensitive_columns": ["gender"],
        },
    )
    assert audit_response.status_code == 200
    audit_id = audit_response.json()["data"]["audit_id"]
    assert audit_id.startswith("audit_")

    report_response = client.post(
        "/api/v1/generate-report",
        json={"project_id": project_id, "audit_id": audit_id, "mode": "executive"},
    )
    assert report_response.status_code == 200
    body = report_response.json()
    assert body["success"] is True
    assert body["data"]["report_id"].startswith("report_")

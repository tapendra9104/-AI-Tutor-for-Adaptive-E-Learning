from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_login_returns_bearer_token_and_profile():
    response = client.post(
        "/api/auth/login",
        json={"email": "ananya@tutorflow.dev", "password": "demo123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "ananya@tutorflow.dev"
    assert payload["user"]["student_id"] == "student-1"


def test_dashboard_requires_authentication():
    response = client.get("/api/students/student-1/dashboard")

    assert response.status_code == 401


def test_student_cannot_access_another_student_dashboard():
    login = client.post(
        "/api/auth/login",
        json={"email": "rahul@tutorflow.dev", "password": "demo123"},
    )
    token = login.json()["access_token"]

    response = client.get(
        "/api/students/student-1/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


from app.core.security import create_access_token
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import AIServiceError


def auth_headers(user_id):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def create_user(test_database):
    db = test_database()

    user = User(
        full_name="Generation Test User",
        email="generation@test.com",
        hashed_password="test-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    return user_id


def test_generate_code_success(client, test_database, monkeypatch):
    user_id = create_user(test_database)

    async def mock_generate_code(prompt):
        return {
            "code": "print('Generated successfully')",
            "model": "mock",
            "provider": "mock",
        }

    monkeypatch.setattr(
        "app.api.routes.generate.generate_code",
        mock_generate_code,
    )

    response = client.post(
        "/api/v1/generate",
        headers=auth_headers(user_id),
        json={"prompt": "Print a success message"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["generated_code"] == "print('Generated successfully')"
    assert data["model_name"] == "mock"
    assert data["generation_status"] == "completed"


def test_generate_code_failure_marks_task_failed(
    client,
    test_database,
    monkeypatch,
):
    user_id = create_user(test_database)

    async def mock_generate_code(prompt):
        raise AIServiceError("Simulated provider failure")

    monkeypatch.setattr(
        "app.api.routes.generate.generate_code",
        mock_generate_code,
    )

    response = client.post(
        "/api/v1/generate",
        headers=auth_headers(user_id),
        json={"prompt": "Generate a Python program"},
    )

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "Code generation failed. Please try again."
    )

    db = test_database()

    task = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .first()
    )

    assert task is not None
    assert task.generation_status == "failed"
    assert task.generated_code is None
    assert task.model_name is None

    db.close()


def test_generate_code_unexpected_error_returns_500(
    client,
    test_database,
    monkeypatch,
):
    user_id = create_user(test_database)

    async def mock_generate_code(prompt):
        raise RuntimeError("Internal secret error")

    monkeypatch.setattr(
        "app.api.routes.generate.generate_code",
        mock_generate_code,
    )

    response = client.post(
        "/api/v1/generate",
        headers=auth_headers(user_id),
        json={"prompt": "Generate a Python program"},
    )

    assert response.status_code == 500
    assert "Internal secret error" not in response.text


def test_generate_code_requires_authentication(client):
    response = client.post(
        "/api/v1/generate",
        json={"prompt": "Print hello"},
    )

    assert response.status_code in (401, 403)

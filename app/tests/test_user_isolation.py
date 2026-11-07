
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.database.connection import Base, get_db
from app.models.user import User
from app.models.task import Task
from app.models.execution import Execution


@pytest.fixture
def test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_database, monkeypatch):
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-only-secret-key-for-proofrun",
    )

    def override_get_db():
        db = test_database()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def two_users(test_database):
    db = test_database()

    user_a = User(
        full_name="User A",
        email="usera@test.com",
        hashed_password="test-hash-a",
    )

    user_b = User(
        full_name="User B",
        email="userb@test.com",
        hashed_password="test-hash-b",
    )

    db.add_all([user_a, user_b])
    db.commit()

    db.refresh(user_a)
    db.refresh(user_b)

    user_a_id = user_a.id
    user_b_id = user_b.id

    task_a = Task(
        user_id=user_a_id,
        prompt="Task belonging to User A",
        generated_code="print('User A')",
        model_name="mock",
        generation_status="completed",
    )

    task_b = Task(
        user_id=user_b_id,
        prompt="Task belonging to User B",
        generated_code="print('User B')",
        model_name="mock",
        generation_status="completed",
    )

    db.add_all([task_a, task_b])
    db.commit()

    db.refresh(task_a)
    db.refresh(task_b)

    task_a_id = task_a.id
    task_b_id = task_b.id

    execution_a = Execution(
        task_id=task_a_id,
        user_id=user_a_id,
        status="success",
        stdout="User A output",
        exit_code=0,
    )

    execution_b = Execution(
        task_id=task_b_id,
        user_id=user_b_id,
        status="success",
        stdout="User B output",
        exit_code=0,
    )

    db.add_all([execution_a, execution_b])
    db.commit()
    db.close()

    return {
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "task_a_id": task_a_id,
        "task_b_id": task_b_id,
    }


def auth_headers(user_id):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def test_user_can_only_see_own_tasks(client, two_users):
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers(two_users["user_a_id"]),
    )

    assert response.status_code == 200

    returned_ids = [task["id"] for task in response.json()]

    assert two_users["task_a_id"] in returned_ids
    assert two_users["task_b_id"] not in returned_ids


def test_user_can_only_see_own_executions(client, two_users):
    response = client.get(
        "/api/v1/executions",
        headers=auth_headers(two_users["user_a_id"]),
    )

    assert response.status_code == 200

    returned_task_ids = [
        execution["task_id"]
        for execution in response.json()
    ]

    assert two_users["task_a_id"] in returned_task_ids
    assert two_users["task_b_id"] not in returned_task_ids


def test_user_cannot_execute_another_users_task(
    client,
    two_users,
    monkeypatch,
):
    def unexpected_execution(*args, **kwargs):
        pytest.fail("Sandbox must not execute another user's task")

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        unexpected_execution,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(two_users["user_a_id"]),
        json={
            "task_id": two_users["task_b_id"],
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_unauthenticated_user_cannot_access_task_history(client):
    response = client.get("/api/v1/tasks")

    assert response.status_code in (401, 403)


def test_unauthenticated_user_cannot_access_execution_history(client):
    response = client.get("/api/v1/executions")

    assert response.status_code in (401, 403)

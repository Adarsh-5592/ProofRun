from app.core.security import create_access_token
from app.models.execution import Execution
from app.models.task import Task
from app.models.user import User


def auth_headers(user_id):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def create_user_and_task(test_database):
    db = test_database()

    user = User(
        full_name="Execution Test User",
        email="execution-test@example.com",
        hashed_password="test-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    task = Task(
        user_id=user.id,
        prompt="Print Hello World",
        generated_code="print('Hello World')",
        model_name="mock",
        generation_status="completed",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    user_id = user.id
    task_id = task.id

    db.close()

    return user_id, task_id


def test_successful_execution_is_saved(
    client,
    test_database,
    monkeypatch,
):
    user_id, task_id = create_user_and_task(test_database)

    def fake_run_code(code, timeout_seconds):
        assert code == "print('Hello World')"
        assert timeout_seconds == 10

        return {
            "status": "success",
            "stdout": "Hello World\n",
            "stderr": "",
            "exit_code": 0,
            "timed_out": False,
            "output_limited": False,
            "oom_killed": False,
            "cleanup_ok": True,
            "duration_ms": 100,
            "error": None,
        }

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        fake_run_code,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(user_id),
        json={
            "task_id": task_id,
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["task_id"] == task_id
    assert data["status"] == "success"
    assert data["stdout"] == "Hello World\n"
    assert data["exit_code"] == 0
    assert data["cleanup_ok"] is True

    db = test_database()

    saved_execution = (
        db.query(Execution)
        .filter(Execution.id == data["id"])
        .first()
    )

    assert saved_execution is not None
    assert saved_execution.user_id == user_id
    assert saved_execution.status == "success"

    db.close()


def test_busy_sandbox_result_is_saved(
    client,
    test_database,
    monkeypatch,
):
    user_id, task_id = create_user_and_task(test_database)

    def fake_run_code(code, timeout_seconds):
        return {
            "status": "busy",
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "timed_out": False,
            "output_limited": False,
            "oom_killed": False,
            "cleanup_ok": True,
            "duration_ms": 1000,
            "error": "Sandbox is busy. Please try again shortly.",
        }

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        fake_run_code,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(user_id),
        json={
            "task_id": task_id,
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "busy"
    assert "busy" in response.json()["error"].lower()


def test_unexpected_sandbox_exception_is_handled(
    client,
    test_database,
    monkeypatch,
):
    user_id, task_id = create_user_and_task(test_database)

    def failing_run_code(*args, **kwargs):
        raise RuntimeError("Internal Docker details")

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        failing_run_code,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(user_id),
        json={
            "task_id": task_id,
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "sandbox_error"
    assert data["error"] == "Sandbox execution failed unexpectedly."
    assert "Internal Docker details" not in str(data)

    db = test_database()

    saved_execution = (
        db.query(Execution)
        .filter(Execution.id == data["id"])
        .first()
    )

    assert saved_execution is not None
    assert saved_execution.status == "sandbox_error"

    db.close()


def test_task_without_generated_code_is_not_executed(
    client,
    test_database,
    monkeypatch,
):
    db = test_database()

    user = User(
        full_name="Incomplete Task User",
        email="incomplete-task@example.com",
        hashed_password="test-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    task = Task(
        user_id=user.id,
        prompt="Incomplete task",
        generated_code=None,
        model_name=None,
        generation_status="failed",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    user_id = user.id
    task_id = task.id

    db.close()

    def unexpected_execution(*args, **kwargs):
        raise AssertionError("Sandbox must not execute incomplete tasks")

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        unexpected_execution,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(user_id),
        json={
            "task_id": task_id,
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Task has no successfully generated code"
    )


def test_unauthenticated_user_cannot_execute_code(client):
    response = client.post(
        "/api/v1/execute",
        json={
            "task_id": "00000000-0000-0000-0000-000000000000",
            "timeout_seconds": 10,
        },
    )

    assert response.status_code in (401, 403)

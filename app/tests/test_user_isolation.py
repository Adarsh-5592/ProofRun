
from app.core.security import create_access_token
from app.models.user import User
from app.models.task import Task
from app.models.execution import Execution


def auth_headers(user_id):
    token = create_access_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def test_user_can_only_see_own_tasks(client, test_database):
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
    db.close()

    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers(user_a_id),
    )

    assert response.status_code == 200

    returned_ids = [task["id"] for task in response.json()]

    assert task_a_id in returned_ids
    assert task_b_id not in returned_ids


def test_user_can_only_see_own_executions(client, test_database):
    db = test_database()

    user_a = User(
        full_name="User A",
        email="executiona@test.com",
        hashed_password="test-hash-a",
    )

    user_b = User(
        full_name="User B",
        email="executionb@test.com",
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
        prompt="Task A",
        generated_code="print('A')",
        model_name="mock",
        generation_status="completed",
    )

    task_b = Task(
        user_id=user_b_id,
        prompt="Task B",
        generated_code="print('B')",
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

    response = client.get(
        "/api/v1/executions",
        headers=auth_headers(user_a_id),
    )

    assert response.status_code == 200

    returned_task_ids = [
        execution["task_id"]
        for execution in response.json()
    ]

    assert task_a_id in returned_task_ids
    assert task_b_id not in returned_task_ids


def test_user_cannot_execute_another_users_task(
    client,
    test_database,
    monkeypatch,
):
    db = test_database()

    user_a = User(
        full_name="User A",
        email="executea@test.com",
        hashed_password="test-hash-a",
    )

    user_b = User(
        full_name="User B",
        email="executeb@test.com",
        hashed_password="test-hash-b",
    )

    db.add_all([user_a, user_b])
    db.commit()

    db.refresh(user_a)
    db.refresh(user_b)

    user_a_id = user_a.id
    user_b_id = user_b.id

    task_b = Task(
        user_id=user_b_id,
        prompt="Private task belonging to User B",
        generated_code="print('User B')",
        model_name="mock",
        generation_status="completed",
    )

    db.add(task_b)
    db.commit()
    db.refresh(task_b)

    task_b_id = task_b.id
    db.close()

    def unexpected_execution(*args, **kwargs):
        raise AssertionError(
            "Sandbox must not execute another user's task"
        )

    monkeypatch.setattr(
        "app.api.routes.execute.run_code",
        unexpected_execution,
    )

    response = client.post(
        "/api/v1/execute",
        headers=auth_headers(user_a_id),
        json={
            "task_id": task_b_id,
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


def test_failed_generation_task_appears_in_task_history(
    client,
    test_database,
):
    db = test_database()

    user = User(
        full_name="Failed Generation User",
        email="failed@test.com",
        hashed_password="test-hash",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    failed_task = Task(
        user_id=user_id,
        prompt="Generate a Python program",
        generated_code=None,
        model_name=None,
        generation_status="failed",
    )

    db.add(failed_task)
    db.commit()
    db.refresh(failed_task)

    task_id = failed_task.id
    db.close()

    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers(user_id),
    )

    assert response.status_code == 200

    tasks = response.json()

    returned_task = next(
        task for task in tasks if task["id"] == task_id
    )

    assert returned_task["generation_status"] == "failed"
    assert returned_task["generated_code"] is None

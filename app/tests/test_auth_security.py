
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.rate_limiter import limiter

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.database.connection import Base, get_db
from app.models.user import User


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


def test_missing_token_returns_401(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_invalid_token_returns_401(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_expired_token_returns_401(client, monkeypatch):
    import jwt

    secret = "test-only-secret-key-for-proofrun"

    monkeypatch.setattr(settings, "jwt_secret_key", secret)

    expired_payload = {
        "sub": "1",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    token = jwt.encode(
        expired_payload,
        secret,
        algorithm="HS256",
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_inactive_user_cannot_access_profile(client, test_database):
    db = test_database()

    user = User(
        full_name="Inactive User",
        email="inactive@test.com",
        hashed_password="test-hash",
        is_active=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id
    db.close()

    token = create_access_token(user_id)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {
            "full_name": "Test User",
            "email": "short@test.com",
            "password": "Short1",
        },
        {
            "full_name": "Test User",
            "email": "nondigit@test.com",
            "password": "LongPasswordOnly",
        },
        {
            "full_name": "   ",
            "email": "whitespace@test.com",
            "password": "LongPassword123",
        },
    ],
)
def test_invalid_registration_data_is_rejected(client, payload):
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


def test_registration_normalizes_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "  Test   User  ",
            "email": "TESTUSER@EXAMPLE.COM",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert response.json()["full_name"] == "Test User"

def test_login_rate_limit_blocks_sixth_attempt(client):
    # Clear previous rate-limit state for an isolated test.
    limiter._storage.reset()

    try:
        payload = {
            "email": "unknown@test.com",
            "password": "WrongPassword123",
        }

        # First five attempts should reach the login handler.
        for _ in range(5):
            response = client.post("/api/v1/auth/login", json=payload)
            assert response.status_code == 401

        # Sixth attempt should be rate-limited.
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 429

    finally:
        limiter._storage.reset()

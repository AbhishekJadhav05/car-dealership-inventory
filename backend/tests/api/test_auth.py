"""API tests for the auth endpoints.

Covers the full HTTP contract:  register, login, and /me.
All tests run against a real Postgres session that is rolled back on teardown.
"""

from fastapi.testclient import TestClient

_REGISTER_URL = "/api/auth/register"
_LOGIN_URL = "/api/auth/login"
_ME_URL = "/api/auth/me"

_VALID_EMAIL = "alice@example.com"
_VALID_PASSWORD = "secret123"


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------


def test_register_returns_201_with_user(client: TestClient) -> None:
    resp = client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})

    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == _VALID_EMAIL
    assert body["role"] == "customer"
    assert "id" in body


def test_register_returns_409_on_duplicate_email(client: TestClient) -> None:
    client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})

    resp = client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": "other"})

    assert resp.status_code == 409


def test_register_returns_422_on_invalid_email(client: TestClient) -> None:
    resp = client.post(_REGISTER_URL, json={"email": "not-an-email", "password": _VALID_PASSWORD})

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------


def test_login_returns_200_with_bearer_token(client: TestClient) -> None:
    client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})

    resp = client.post(_LOGIN_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_returns_401_on_wrong_password(client: TestClient) -> None:
    client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})

    resp = client.post(_LOGIN_URL, json={"email": _VALID_EMAIL, "password": "wrong"})

    assert resp.status_code == 401


def test_login_returns_401_on_unknown_email(client: TestClient) -> None:
    resp = client.post(_LOGIN_URL, json={"email": "nobody@example.com", "password": "secret"})

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------


def test_me_returns_current_user(client: TestClient) -> None:
    client.post(_REGISTER_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})
    login_resp = client.post(_LOGIN_URL, json={"email": _VALID_EMAIL, "password": _VALID_PASSWORD})
    token = login_resp.json()["access_token"]

    resp = client.get(_ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == _VALID_EMAIL
    assert body["role"] == "customer"


def test_me_returns_401_without_token(client: TestClient) -> None:
    resp = client.get(_ME_URL)

    assert resp.status_code == 401

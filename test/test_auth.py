"""
End-to-end authentication flow tests.
Covers all 6 mandatory test scenarios from spec §4.

Test order matters — each step builds on the state from the previous one.
Uses module-scoped state dict to share tokens across test functions.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient

# Module-level state shared across the ordered test steps
_state: dict = {}

# ── Test credentials (unique per run to avoid collisions in a shared DB) ──────
import uuid
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "SecurePassword123!"


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1 — Registration
# Spec §4: POST /auth/register → DB record created, UserRegistrationResponse returned
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step1_register(client: AsyncClient):
    """User can register with a valid email and password >= 8 chars."""
    response = await client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 201, response.text

    data = response.json()
    assert "id" in data
    assert data["email"] == TEST_EMAIL
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "created_at" in data

    _state["user_id"] = data["id"]


@pytest.mark.asyncio
async def test_step1_register_duplicate(client: AsyncClient):
    """Registering with an already-used email must return HTTP 400."""
    response = await client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 — Authentication / Login
# Spec §4: POST /auth/login → both access_token and refresh_token returned
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step2_login(client: AsyncClient):
    """Valid credentials return a dual-token pair with token_type 'bearer'."""
    response = await client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    _state["access_token"] = data["access_token"]
    _state["refresh_token"] = data["refresh_token"]


@pytest.mark.asyncio
async def test_step2_login_wrong_password(client: AsyncClient):
    """Wrong password must return HTTP 401."""
    response = await client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": "WrongPassword!"}
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3 — Security-Aware Protected Endpoint
# Spec §4: Authenticated GET /auth/me returns the correct user context
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step3_protected_endpoint_with_valid_token(client: AsyncClient):
    """A valid access token gives access to the /auth/me self-context endpoint."""
    token = _state["access_token"]
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_step3_protected_endpoint_without_token(client: AsyncClient):
    """Accessing /auth/me without a token must return HTTP 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4 — Token Rotation / Refresh
# Spec §4: POST /auth/refresh → new token pair without losing user identity
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step4_token_refresh(client: AsyncClient):
    """Refresh token produces a new token pair; user identity is preserved."""
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": _state["refresh_token"]}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Store rotated tokens for subsequent steps
    _state["access_token"] = data["access_token"]
    _state["refresh_token"] = data["refresh_token"]

    # Verify identity preserved — new token still grants access to /auth/me
    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == TEST_EMAIL


@pytest.mark.asyncio
async def test_step4_invalid_refresh_token(client: AsyncClient):
    """An invalid/tampered refresh token must return HTTP 401."""
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "this.is.not.a.valid.token"}
    )
    assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Step 5 — Logout / Blacklisting
# Spec §4: POST /auth/logout → blacklist entry created, GenericActionResponse returned
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step5_logout(client: AsyncClient):
    """Logout returns GenericActionResponse with 'message' field and HTTP 200."""
    token = _state["access_token"]
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text

    data = response.json()
    # Spec §3.3: response must contain 'message' key
    assert "message" in data
    assert data["message"] == "Successfully logged out"

    # Preserve the logged-out token for Step 6
    _state["revoked_token"] = token


# ═══════════════════════════════════════════════════════════════════════════════
# Step 6 — Zero-Trust Post-Validation (Blacklisted Token Must Be Rejected)
# Spec §4: Reusing a blacklisted token → HTTP 401, must NOT hit the DB
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_step6_blacklisted_token_rejected(client: AsyncClient):
    """A token that was used for logout must be rejected with HTTP 401 on all subsequent requests."""
    revoked_token = _state["revoked_token"]

    # Attempt to access protected endpoint with the revoked token
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {revoked_token}"}
    )
    assert response.status_code == 401, response.text

    detail = response.json().get("detail", "")
    assert "revoked" in detail.lower(), (
        f"Expected 'revoked' in error detail, got: '{detail}'"
    )

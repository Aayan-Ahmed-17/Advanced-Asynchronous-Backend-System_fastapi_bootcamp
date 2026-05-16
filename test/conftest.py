"""
Shared pytest fixtures for the auth test suite.
Uses httpx.AsyncClient with the FastAPI app in-process (no live server needed).
"""
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture(scope="module")
async def client():
    """Provides an async test client that exercises the full ASGI stack."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

"""
Shared pytest fixtures for the auth test suite.
Uses httpx.AsyncClient with the FastAPI app in-process (no live server needed).
"""
# pyrefly: ignore [missing-import]
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config.database import init_db, close_db
from app.config.cache import init_redis, close_redis


@pytest_asyncio.fixture(autouse=True)
async def initialize_connections():
    """Ensures DB and Redis are connected before any tests run."""
    await init_db()
    await init_redis()
    yield
    await close_db()
    await close_redis()


@pytest_asyncio.fixture
async def client():
    """Provides an async test client that exercises the full ASGI stack."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import init_db, close_db
from app.config.cache import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connections
    await init_db()
    await init_redis()
    print("Successfully connected to MongoDB and Redis")
    yield
    # Shutdown: Close connections
    await close_db()
    await close_redis()
    print("Closed MongoDB and Redis connections")

app = FastAPI(
    title="Advanced Asynchronous Backend System (Enterprise Core)",
    description="High-performance, non-blocking asynchronous security and user routing engine.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Enterprise Core Auth API"}

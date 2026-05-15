from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import init_db, close_db
from app.config.cache import init_redis, close_redis
from app.routes.auth_routes import router as auth_router

from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connections
    await init_db()
    await init_redis()
    logger.info("Successfully connected to MongoDB and Redis")
    yield
    # Shutdown: Close connections
    await close_db()
    await close_redis()
    logger.info("Closed MongoDB and Redis connections")

app = FastAPI(
    title="Advanced Asynchronous Backend System (Enterprise Core)",
    description="High-performance, non-blocking asynchronous security and user routing engine.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Enterprise Core Auth API"}

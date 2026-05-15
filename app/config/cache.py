import redis.asyncio as redis
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

# Redis client will be initialized in the FastAPI lifespan
redis_client: redis.Redis = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

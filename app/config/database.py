# pyrefly: ignore [missing-import]
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# We will initialize these properly to manage pool lifecycle
client: AsyncMongoClient = None
db = None
user_collection = None

async def init_db():
    global client, db, user_collection
    client = AsyncMongoClient(MONGO_URI)
    db = client.advanved_core_auth
    user_collection = db["user"]

async def close_db():
    global client
    if client:
        await client.close()
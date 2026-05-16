# pyrefly: ignore [missing-import]
from pymongo import AsyncMongoClient, ReturnDocument
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
    db = client.advanced_core_auth
    user_collection = db["user"]

async def close_db():
    global client
    if client:
        await client.close()

def get_user_collection():
    return user_collection

async def get_next_sequence_value(sequence_name: str):
    """Atomic counter for sequential IDs."""
    global db
    result = await db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result["sequence_value"]
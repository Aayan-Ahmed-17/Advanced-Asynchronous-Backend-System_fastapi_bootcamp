from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Create a MongoDB client
client = MongoClient(MONGO_URI)

# Define database and collection
db = client.advanved_core_auth
user_collection = db["user"]
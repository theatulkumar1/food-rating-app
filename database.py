"""
MongoDB Database Configuration for Campus Food Backend
Uses Motor (async MongoDB driver) for FastAPI
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campus_food")

# Global variables for database connection
mongodb_client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global mongodb_client, database
    try:
        mongodb_client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=45000
        )
        # Test connection
        await mongodb_client.admin.command('ping')
        database = mongodb_client[DATABASE_NAME]
        print(" MongoDB Connected Successfully")
        print(f" Database: {DATABASE_NAME}")
    except ServerSelectionTimeoutError as e:
        print(f" MongoDB Connection Error: {e}")
        raise
    except Exception as e:
        print(f" Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print(" MongoDB connection closed")


def get_database():
    """Get database instance"""
    return database


# Collection names
COLLECTIONS = {
    "stores": "stores",
    "users": "users",
    "reviews": "reviews",
    "orders": "orders",
    "active_users": "active_users",
    "store_registrations": "store_registrations"
}


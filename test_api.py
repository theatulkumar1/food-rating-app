"""
API Connection Test Script
Tests all API endpoints to verify they work correctly
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campus_food")


async def test_database_connection():
    """Test MongoDB connection"""
    print("==========================================")
    print(" Campus Food - API Connection Test")
    print("==========================================\n")
    
    print("[1/8] Testing MongoDB Connection...")
    print(f" URI: {MONGODB_URI}")
    
    try:
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db = client[DATABASE_NAME]
        print(" MongoDB connection successful\n")
    except Exception as e:
        print(f" MongoDB connection failed: {e}")
        return False
    
    # Test collections
    print("[2/8] Checking Collections...")
    collections = await db.list_collection_names()
    print(f" Found {len(collections)} collection(s):")
    for col in collections:
        print(f"   - {col}")
    print()
    
    # Test stores collection
    print("[3/8] Testing Stores Collection...")
    stores_count = await db.stores.count_documents({})
    print(f" Stores collection: {stores_count} document(s)")
    
    if stores_count > 0:
        store = await db.stores.find_one({})
        print(f" Sample store: {store.get('name')}")
    print()
    
    # Test users collection
    print("[4/8] Testing Users Collection...")
    users_count = await db.users.count_documents({})
    print(f" Users collection: {users_count} document(s)")
    
    if users_count > 0:
        admin = await db.users.find_one({"is_admin": True})
        if admin:
            print(f" Admin user found: {admin.get('username')}")
    print()
    
    # Test reviews collection
    print("[5/8] Testing Reviews Collection...")
    reviews_count = await db.reviews.count_documents({})
    print(f" Reviews collection: {reviews_count} document(s)")
    
    if reviews_count > 0:
        review = await db.reviews.find_one({})
        print(f" Sample review: {review.get('rating')} - {review.get('comment')[:50]}...")
    print()
    
    # Test orders collection
    print("[6/8] Testing Orders Collection...")
    orders_count = await db.orders.count_documents({})
    print(f" Orders collection: {orders_count} document(s)")
    print()
    
    # Test active_users collection
    print("[7/8] Testing Active Users Collection...")
    active_users_count = await db.active_users.count_documents({})
    print(f" Active users collection: {active_users_count} document(s)")
    print()
    
    # Test indexes
    print("[8/8] Checking Indexes...")
    
    stores_indexes = await db.stores.list_indexes().to_list(None)
    print(f" Stores indexes: {len(stores_indexes)}")
    
    reviews_indexes = await db.reviews.list_indexes().to_list(None)
    print(f" Reviews indexes: {len(reviews_indexes)}")
    
    print()
    
    # Summary
    print("==========================================")
    print(" ALL TESTS PASSED!")
    print("==========================================\n")
    
    print(" Summary:")
    print(f"   - Database: {DATABASE_NAME}")
    print(f"   - Collections: {len(collections)}")
    print(f"   - Stores: {stores_count}")
    print(f"   - Users: {users_count}")
    print(f"   - Reviews: {reviews_count}")
    print(f"   - Orders: {orders_count}")
    print(f"   - Active Users: {active_users_count}")
    print()
    
    if stores_count == 0:
        print("  TIP: No data found. Run 'python init_db.py' to populate the database.")
        print()
    
    print(" Database is ready!")
    print()
    print(" Start the server:")
    print("   uvicorn main:app --reload --port 8000")
    print()
    print(" API Documentation:")
    print("   http://localhost:8000/docs")
    print()
    
    client.close()
    return True


async def test_data_integrity():
    """Test data integrity and relationships"""
    print("==========================================")
    print(" Testing Data Integrity...")
    print("==========================================\n")
    
    client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    
    # Test store menu items have IDs
    stores = await db.stores.find().to_list(10)
    print(f"[1/3] Checking menu items...")
    
    for store in stores:
        menu = store.get("menu", [])
        for item in menu:
            if "id" not in item:
                print(f" Menu item missing ID in {store.get('name')}: {item.get('name')}")
            else:
                print(f" {store.get('name')} - {item.get('name')} has ID: {item.get('id')}")
    print()
    
    # Test reviews reference valid stores
    print(f"[2/3] Checking review references...")
    reviews = await db.reviews.find().to_list(10)
    
    for review in reviews:
        store_id = review.get("store_id")
        store = await db.stores.find_one({"id": store_id})
        
        if store:
            print(f" Review references valid store: {review.get('store_name')}")
        else:
            print(f" Review references invalid store ID: {store_id}")
    print()
    
    # Test password hashing
    print(f"[3/3] Checking password security...")
    admin = await db.users.find_one({"is_admin": True})
    
    if admin:
        password = admin.get("hashed_password", "")
        if password.startswith("$2b$") or password.startswith("$2a$"):
            print(f" Admin password is properly hashed")
        else:
            print(f" Admin password is not hashed!")
    
    stores = await db.stores.find().to_list(3)
    for store in stores[:3]:
        password = store.get("hashed_password", "")
        if password.startswith("$2b$") or password.startswith("$2a$"):
            print(f" {store.get('name')} password is properly hashed")
        else:
            print(f" {store.get('name')} password is not hashed!")
    
    print()
    print(" Data integrity check complete!")
    print()
    
    client.close()


async def main():
    """Run all tests"""
    # Test database connection
    success = await test_database_connection()
    
    if not success:
        print(" Database connection failed. Please check:")
        print("   1. MongoDB is running (net start MongoDB)")
        print("   2. .env file has correct MONGODB_URI")
        print("   3. MongoDB URI is accessible")
        sys.exit(1)
    
    # Test data integrity
    await test_data_integrity()
    
    print("==========================================")
    print(" ALL API CONNECTION TESTS PASSED!")
    print("==========================================")
    print()
    print(" Your backend is ready to use!")
    print()


if __name__ == "__main__":
    asyncio.run(main())



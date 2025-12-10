"""
Database Initialization and Seeding Script
Populates MongoDB with initial data for Campus Food
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campus_food")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def init_database():
    """Initialize database with seed data"""
    
    print("==========================================")
    print("🌱 Campus Food - Database Initialization")
    print("==========================================\n")
    
    # Connect to MongoDB
    print("[1/6] Connecting to MongoDB...")
    print(f"📍 URI: {MONGODB_URI}")
    
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connected successfully\n")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return
    
    # Clear existing data
    print("[2/6] Clearing existing data...")
    await db.stores.delete_many({})
    await db.users.delete_many({})
    await db.reviews.delete_many({})
    await db.orders.delete_many({})
    await db.active_users.delete_many({})
    await db.store_registrations.delete_many({})
    print("✅ Existing data cleared\n")
    
    # Create admin user
    print("[3/6] Creating admin user...")
    admin_user = {
        "username": "admin",
        "email": "admin@campusfood.com",
        "phone": "+1234567890",
        "hashed_password": hash_password("admin123"),
        "is_admin": True,
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(admin_user)
    print("✅ Admin user created (admin / admin123)\n")
    
    # Create test users
    print("[4/6] Creating test users...")
    test_users = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "phone": "+1234567891",
            "hashed_password": hash_password("user123"),
            "is_admin": False,
            "created_at": datetime.utcnow()
        },
        {
            "username": "jane_smith",
            "email": "jane@example.com",
            "phone": "+1234567892",
            "hashed_password": hash_password("user123"),
            "is_admin": False,
            "created_at": datetime.utcnow()
        }
    ]
    await db.users.insert_many(test_users)
    print(f"✅ Created {len(test_users)} test users\n")
    
    # Create stores
    print("[5/6] Creating stores with menu items...")
    stores_data = [
        {
            "id": 1,
            "name": "GREEN CHILLIES",
            "store_id": "greenchillies",
            "hashed_password": hash_password("store123"),
            "email": "greenchillies@campus.com",
            "phone": "+1234567801",
            "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800",
            "rating": 4.5,
            "tagline": "Spicy & Tasty Fast Food",
            "gradient": "from-orange-200 to-red-300",
            "is_open": True,
            "reviews": 245,
            "menu": [
                {"id": 1, "name": "Spicy Chicken Burger", "price": 120, "is_popular": True, "rating": 4.6, "review_count": 45, "category": "Fast Food"},
                {"id": 2, "name": "Veg Momos", "price": 60, "rating": 4.3, "review_count": 32, "category": "Fast Food"},
                {"id": 3, "name": "Paneer Tikka Roll", "price": 90, "is_favorite": True, "rating": 4.7, "review_count": 51, "category": "Fast Food"},
                {"id": 4, "name": "Green Salad Bowl", "price": 80, "rating": 4.2, "review_count": 28, "category": "Healthy"},
                {"id": 5, "name": "French Fries", "price": 50, "is_popular": True, "rating": 4.4, "review_count": 67, "category": "Fast Food"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.5},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 2,
            "name": "THE HEALTHY HUT",
            "store_id": "healthyhut",
            "hashed_password": hash_password("store123"),
            "email": "healthyhut@campus.com",
            "phone": "+1234567802",
            "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800",
            "rating": 4.7,
            "tagline": "Fresh & Nutritious Meals",
            "gradient": "from-green-200 to-emerald-300",
            "is_open": True,
            "reviews": 318,
            "menu": [
                {"id": 1, "name": "Quinoa Power Bowl", "price": 150, "is_popular": True, "rating": 4.8, "review_count": 89, "category": "Healthy"},
                {"id": 2, "name": "Greek Salad", "price": 110, "rating": 4.6, "review_count": 76, "category": "Healthy"},
                {"id": 3, "name": "Avocado Toast", "price": 130, "is_favorite": True, "rating": 4.7, "review_count": 95, "category": "Healthy"},
                {"id": 4, "name": "Fresh Fruit Smoothie", "price": 90, "is_popular": True, "rating": 4.5, "review_count": 62, "category": "Beverages"},
                {"id": 5, "name": "Grilled Chicken Salad", "price": 140, "rating": 4.6, "review_count": 58, "category": "Healthy"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.7},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 3,
            "name": "BIG TREAT",
            "store_id": "bigtreat",
            "hashed_password": hash_password("store123"),
            "email": "bigtreat@campus.com",
            "phone": "+1234567803",
            "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800",
            "rating": 4.3,
            "tagline": "Pizza & Party Snacks",
            "gradient": "from-yellow-200 to-orange-300",
            "is_open": True,
            "reviews": 189,
            "menu": [
                {"id": 1, "name": "Double Cheese Pizza", "price": 250, "is_popular": True, "rating": 4.7, "review_count": 84, "category": "Fast Food"},
                {"id": 2, "name": "Loaded Nachos", "price": 180, "rating": 4.4, "review_count": 53, "category": "Fast Food"},
                {"id": 3, "name": "Crispy Chicken Wings", "price": 200, "is_favorite": True, "rating": 4.5, "review_count": 68, "category": "Fast Food"},
                {"id": 4, "name": "Chocolate Brownie", "price": 80, "rating": 4.6, "review_count": 72, "category": "Desserts"},
                {"id": 5, "name": "Garlic Bread", "price": 70, "is_popular": True, "rating": 4.3, "review_count": 45, "category": "Fast Food"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.3},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 4,
            "name": "NESCAFE",
            "store_id": "nescafe",
            "hashed_password": hash_password("store123"),
            "email": "nescafe@campus.com",
            "phone": "+1234567804",
            "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
            "rating": 4.6,
            "tagline": "Coffee & Beverages",
            "gradient": "from-amber-200 to-brown-300",
            "is_open": True,
            "reviews": 412,
            "menu": [
                {"id": 1, "name": "Cappuccino", "price": 80, "is_popular": True, "rating": 4.7, "review_count": 94, "category": "Beverages"},
                {"id": 2, "name": "Cold Coffee", "price": 90, "is_favorite": True, "rating": 4.8, "review_count": 112, "category": "Beverages"},
                {"id": 3, "name": "Espresso", "price": 70, "rating": 4.5, "review_count": 73, "category": "Beverages"},
                {"id": 4, "name": "Chocolate Muffin", "price": 60, "rating": 4.4, "review_count": 65, "category": "Desserts"},
                {"id": 5, "name": "Green Tea", "price": 50, "is_popular": True, "rating": 4.3, "review_count": 48, "category": "Beverages"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.6},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 5,
            "name": "HUNGRY NITES",
            "store_id": "hungrynites",
            "hashed_password": hash_password("store123"),
            "email": "hungrynites@campus.com",
            "phone": "+1234567805",
            "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
            "rating": 4.4,
            "tagline": "Late Night Cravings",
            "gradient": "from-purple-200 to-pink-300",
            "is_open": True,
            "reviews": 276,
            "menu": [
                {"id": 1, "name": "Butter Chicken Rice Bowl", "price": 160, "is_popular": True, "rating": 4.7, "review_count": 87, "category": "Fast Food"},
                {"id": 2, "name": "Hakka Noodles", "price": 110, "rating": 4.5, "review_count": 64, "category": "Fast Food"},
                {"id": 3, "name": "Paneer Butter Masala", "price": 140, "is_favorite": True, "rating": 4.6, "review_count": 71, "category": "Fast Food"},
                {"id": 4, "name": "Veg Fried Rice", "price": 100, "rating": 4.4, "review_count": 56, "category": "Fast Food"},
                {"id": 5, "name": "Raita", "price": 40, "rating": 4.2, "review_count": 39, "category": "Fast Food"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.4},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": 6,
            "name": "VIBE SYNC",
            "store_id": "vibesync",
            "hashed_password": hash_password("store123"),
            "email": "vibesync@campus.com",
            "phone": "+1234567806",
            "image": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=800",
            "rating": 4.5,
            "tagline": "Shakes & Smoothies",
            "gradient": "from-cyan-200 to-blue-300",
            "is_open": True,
            "reviews": 198,
            "menu": [
                {"id": 1, "name": "Strawberry Shake", "price": 100, "is_popular": True, "rating": 4.7, "review_count": 65, "category": "Beverages"},
                {"id": 2, "name": "Oreo Milkshake", "price": 120, "is_favorite": True, "rating": 4.8, "review_count": 78, "category": "Beverages"},
                {"id": 3, "name": "Vanilla Ice Cream", "price": 70, "rating": 4.5, "review_count": 54, "category": "Desserts"},
                {"id": 4, "name": "Chocolate Sundae", "price": 110, "rating": 4.6, "review_count": 61, "category": "Desserts"},
                {"id": 5, "name": "Fresh Lemonade", "price": 60, "is_popular": True, "rating": 4.4, "review_count": 47, "category": "Beverages"},
            ],
            "stats": {"total_orders": 0, "total_revenue": 0, "average_rating": 4.5},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.stores.insert_many(stores_data)
    print(f"✅ Created {len(stores_data)} stores with menu items\n")
    
    # Create sample reviews
    print("[6/6] Creating sample reviews...")
    reviews_data = [
        {
            "store_id": 1,
            "store_name": "GREEN CHILLIES",
            "item_id": 1,
            "item_name": "Spicy Chicken Burger",
            "rating": 5,
            "comment": "Absolutely delicious! The chicken was perfectly spiced and juicy. Best burger on campus!",
            "user_name": "john_doe",
            "user_avatar": "👨",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "store_id": 1,
            "store_name": "GREEN CHILLIES",
            "item_id": 3,
            "item_name": "Paneer Tikka Roll",
            "rating": 5,
            "comment": "Amazing flavor! The paneer is so well marinated. My go-to meal!",
            "user_name": "jane_smith",
            "user_avatar": "👩",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "store_id": 2,
            "store_name": "THE HEALTHY HUT",
            "item_id": 1,
            "item_name": "Quinoa Power Bowl",
            "rating": 5,
            "comment": "Perfect for a healthy lunch! Fresh ingredients and great portion size.",
            "user_name": "john_doe",
            "user_avatar": "👨",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "store_id": 4,
            "store_name": "NESCAFE",
            "item_id": 2,
            "item_name": "Cold Coffee",
            "rating": 5,
            "comment": "Best cold coffee on campus! Perfect blend, not too sweet.",
            "user_name": "jane_smith",
            "user_avatar": "👩",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.reviews.insert_many(reviews_data)
    print(f"✅ Created {len(reviews_data)} sample reviews\n")
    
    # Create indexes
    print("Creating database indexes...")
    await db.reviews.create_index([("store_id", 1)])
    await db.reviews.create_index([("item_id", 1)])
    await db.reviews.create_index([("user_name", 1)])
    await db.reviews.create_index([("created_at", -1)])
    await db.active_users.create_index([("user_id", 1)], unique=True)
    await db.active_users.create_index([("last_activity", 1)])
    await db.stores.create_index([("id", 1)], unique=True)
    await db.stores.create_index([("store_id", 1)], unique=True)
    print("✅ Indexes created\n")
    
    # Summary
    print("==========================================")
    print("✅ DATABASE INITIALIZATION COMPLETE!")
    print("==========================================\n")
    
    print("📊 Summary:")
    print(f"   - Stores: {len(stores_data)}")
    print(f"   - Users: {len(test_users) + 1} (1 admin + {len(test_users)} test users)")
    print(f"   - Reviews: {len(reviews_data)}")
    print("")
    
    print("🔐 Login Credentials:")
    print("   Admin:  admin / admin123")
    print("   User:   john_doe / user123")
    print("   Store:  greenchillies / store123")
    print("   Store:  healthyhut / store123")
    print("   Store:  bigtreat / store123")
    print("   Store:  nescafe / store123")
    print("   Store:  hungrynites / store123")
    print("   Store:  vibesync / store123")
    print("")
    
    print("✨ You can now start the server!")
    print("   python -m uvicorn main:app --reload --port 8000")
    print("")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(init_database())

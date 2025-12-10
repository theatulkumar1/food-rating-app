"""
Campus Food Backend API - FastAPI with MongoDB
Main application entry point with all API routes
"""

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import os

# Import database and models
from database import connect_to_mongo, close_mongo_connection, get_database, COLLECTIONS
import models
import schemas

# Create FastAPI app
app = FastAPI(
    title="Campus Food API",
    description="Backend API for Campus Food Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)


# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = get_database()
    try:
        await db.command("ping")
        mongo_status = "Connected"
    except Exception:
        mongo_status = "Disconnected"
    
    return {
        "status": "OK",
        "message": "Campus Food Backend is running",
        "timestamp": datetime.utcnow().isoformat(),
        "mongodb": mongo_status
    }


# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/login", response_model=models.LoginResponse)
async def login(login_data: models.LoginRequest):
    """User/Store/Admin login"""
    db = get_database()
    username = login_data.username.lower().replace(" ", "")
    
    # Check admin credentials
    admin = await db[COLLECTIONS["users"]].find_one({
        "username": login_data.username,
        "is_admin": True
    })
    
    if admin and verify_password(login_data.password, admin.get("hashed_password", "")):
        return models.LoginResponse(
            success=True,
            is_admin=True,
            message="Admin login successful"
        )
    
    # Check store credentials
    store = await db[COLLECTIONS["stores"]].find_one({"store_id": username})
    
    if store and verify_password(login_data.password, store.get("hashed_password", "")):
        return models.LoginResponse(
            success=True,
            is_admin=False,
            store_name=store.get("name"),
            message="Store login successful"
        )
    
    # Regular user login (basic check)
    if login_data.username and login_data.password:
        user = await db[COLLECTIONS["users"]].find_one({"username": login_data.username})
        if user and verify_password(login_data.password, user.get("hashed_password", "")):
            return models.LoginResponse(
                success=True,
                is_admin=False,
                message="User login successful"
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@app.post("/api/auth/register-user")
async def register_user(user_data: models.UserCreate):
    """Register a new user"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db[COLLECTIONS["users"]].find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "phone": user_data.phone,
        "hashed_password": hash_password(user_data.password),
        "is_admin": False,
        "created_at": datetime.utcnow()
    }
    
    result = await db[COLLECTIONS["users"]].insert_one(user_dict)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }


@app.post("/api/auth/register-store")
async def register_store(store_data: models.StoreRegistrationCreate):
    """Register a new store (creates registration request)"""
    db = get_database()
    
    # Validate password match
    if store_data.password != store_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Check if store already exists
    existing_store = await db[COLLECTIONS["stores"]].find_one({
        "$or": [
            {"email": store_data.email},
            {"store_id": store_data.store_id}
        ]
    })
    
    if existing_store:
        raise HTTPException(
            status_code=400,
            detail="Store with this email or store ID already exists"
        )
    
    # Create registration request
    registration_dict = {
        "store_name": store_data.store_name,
        "store_id": store_data.store_id,
        "email": store_data.email,
        "phone": store_data.phone,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db[COLLECTIONS["store_registrations"]].insert_one(registration_dict)
    
    return {
        "success": True,
        "message": "Store registration submitted successfully",
        "registration_id": str(result.inserted_id),
        "status": "pending"
    }


# ==================== STORE ENDPOINTS ====================

@app.get("/api/stores")
async def get_all_stores(open_only: Optional[bool] = Query(None, alias="open")):
    """Get all stores"""
    db = get_database()
    
    # Build query
    query = {}
    if open_only is not None:
        query["is_open"] = open_only
    
    stores_cursor = db[COLLECTIONS["stores"]].find(query)
    stores = await stores_cursor.to_list(length=100)
    
    # Convert ObjectId to string
    result = []
    for store in stores:
        store["_id"] = str(store["_id"])
        # Ensure menu items have proper IDs
        menu = store.get("menu", [])
        for idx, item in enumerate(menu):
            if "id" not in item:
                item["id"] = idx + 1
        result.append(schemas.store_helper(store))
    
    return {"success": True, "data": result}


@app.get("/api/stores/{store_id}")
async def get_store(store_id: int):
    """Get store by ID"""
    db = get_database()
    
    # MongoDB _id or numeric ID
    try:
        store = await db[COLLECTIONS["stores"]].find_one({"_id": ObjectId(store_id)})
    except:
        # Try as numeric ID
        store = await db[COLLECTIONS["stores"]].find_one({"id": store_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    store["_id"] = str(store["_id"])
    return {"success": True, "data": schemas.store_helper(store)}


@app.get("/api/stores/by-name/{store_name}")
async def get_store_by_name(store_name: str):
    """Get store by name"""
    db = get_database()
    
    # Normalize name for search
    normalized_name = store_name.upper().replace(" ", "")
    
    store = await db[COLLECTIONS["stores"]].find_one({
        "name": {"$regex": normalized_name, "$options": "i"}
    })
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    store["_id"] = str(store["_id"])
    return {"success": True, "data": schemas.store_helper(store)}


@app.patch("/api/stores/{store_id}/status")
async def update_store_status(store_id: int, is_open: bool):
    """Toggle store open/closed status"""
    db = get_database()
    
    result = await db[COLLECTIONS["stores"]].update_one(
        {"id": store_id},
        {"$set": {"is_open": is_open, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return {
        "success": True,
        "message": "Store status updated successfully",
        "is_open": is_open
    }


# ==================== MENU ENDPOINTS ====================

@app.get("/api/stores/{store_id}/menu")
async def get_store_menu(store_id: int):
    """Get store menu"""
    db = get_database()
    
    store = await db[COLLECTIONS["stores"]].find_one({"id": store_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return {"success": True, "data": store.get("menu", [])}


@app.put("/api/stores/{store_id}/menu")
async def update_store_menu(store_id: int, menu_items: List[dict]):
    """Update entire store menu"""
    db = get_database()
    
    # Ensure menu items have IDs
    for idx, item in enumerate(menu_items):
        if "id" not in item:
            item["id"] = idx + 1
    
    result = await db[COLLECTIONS["stores"]].update_one(
        {"id": store_id},
        {"$set": {"menu": menu_items, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return {"success": True, "message": "Menu updated successfully"}


@app.put("/api/stores/{store_id}/menu/{item_id}")
async def update_menu_item(store_id: int, item_id: int, item_data: dict):
    """Update a specific menu item"""
    db = get_database()
    
    # Find store
    store = await db[COLLECTIONS["stores"]].find_one({"id": store_id})
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Update menu item
    menu = store.get("menu", [])
    item_found = False
    
    for item in menu:
        if item.get("id") == item_id:
            item.update(item_data)
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Save updated menu
    await db[COLLECTIONS["stores"]].update_one(
        {"id": store_id},
        {"$set": {"menu": menu, "updated_at": datetime.utcnow()}}
    )
    
    return {"success": True, "message": "Menu item updated successfully"}


# ==================== REVIEW ENDPOINTS ====================

@app.get("/api/reviews")
async def get_reviews(
    store_id: Optional[int] = None,
    item_id: Optional[int] = None,
    user_name: Optional[str] = None
):
    """Get all reviews with optional filters"""
    db = get_database()
    
    query = {"status": "approved"}
    if store_id:
        query["store_id"] = store_id
    if item_id:
        query["item_id"] = item_id
    if user_name:
        query["user_name"] = user_name
    
    reviews_cursor = db[COLLECTIONS["reviews"]].find(query).sort("created_at", -1)
    reviews = await reviews_cursor.to_list(length=100)
    
    result = [schemas.review_helper(review) for review in reviews]
    return {"success": True, "data": result}


@app.get("/api/reviews/store/{store_id}")
async def get_store_reviews(store_id: int):
    """Get all reviews for a store"""
    db = get_database()
    
    reviews_cursor = db[COLLECTIONS["reviews"]].find({
        "store_id": store_id,
        "status": "approved"
    }).sort("created_at", -1)
    
    reviews = await reviews_cursor.to_list(length=100)
    result = [schemas.review_helper(review) for review in reviews]
    
    return {"success": True, "data": result}


@app.get("/api/reviews/store/{store_id}/item/{item_id}")
async def get_item_reviews(store_id: int, item_id: int):
    """Get reviews for a specific menu item"""
    db = get_database()
    
    reviews_cursor = db[COLLECTIONS["reviews"]].find({
        "store_id": store_id,
        "item_id": item_id,
        "status": "approved"
    }).sort("created_at", -1)
    
    reviews = await reviews_cursor.to_list(length=100)
    result = [schemas.review_helper(review) for review in reviews]
    
    return {"success": True, "data": result}


@app.post("/api/reviews")
async def create_review(review_data: models.ReviewCreate):
    """Create a new review"""
    db = get_database()
    
    # Create review document
    review_dict = {
        "store_id": review_data.store_id,
        "store_name": review_data.store_name,
        "item_id": review_data.item_id,
        "item_name": review_data.item_name,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "user_name": review_data.user_name,
        "user_avatar": review_data.user_avatar,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db[COLLECTIONS["reviews"]].insert_one(review_dict)
    
    # Update menu item rating
    await update_item_rating(review_data.store_id, review_data.item_id)
    
    review_dict["_id"] = str(result.inserted_id)
    
    return {
        "success": True,
        "message": "Review submitted successfully",
        "data": schemas.review_helper(review_dict)
    }


@app.get("/api/reviews/stats/{store_id}/{item_id}")
async def get_review_stats(store_id: int, item_id: int):
    """Get review statistics for a menu item"""
    db = get_database()
    
    # Get all approved reviews
    reviews_cursor = db[COLLECTIONS["reviews"]].find({
        "store_id": store_id,
        "item_id": item_id,
        "status": "approved"
    })
    
    reviews = await reviews_cursor.to_list(length=1000)
    
    if not reviews:
        return {"success": True, "data": {"rating": 4.0, "count": 0}}
    
    # Calculate average
    total_rating = sum(r["rating"] for r in reviews)
    avg_rating = round(total_rating / len(reviews), 1)
    
    return {
        "success": True,
        "data": {
            "rating": avg_rating,
            "count": len(reviews)
        }
    }


async def update_item_rating(store_id: int, item_id: int):
    """Update menu item rating based on reviews"""
    db = get_database()
    
    # Get all approved reviews for this item
    reviews_cursor = db[COLLECTIONS["reviews"]].find({
        "store_id": store_id,
        "item_id": item_id,
        "status": "approved"
    })
    
    reviews = await reviews_cursor.to_list(length=1000)
    
    if reviews:
        # Calculate average
        total_rating = sum(r["rating"] for r in reviews)
        avg_rating = round(total_rating / len(reviews), 1)
        review_count = len(reviews)
    else:
        avg_rating = 4.0
        review_count = 0
    
    # Update store menu item
    store = await db[COLLECTIONS["stores"]].find_one({"id": store_id})
    if store:
        menu = store.get("menu", [])
        for item in menu:
            if item.get("id") == item_id:
                item["rating"] = avg_rating
                item["review_count"] = review_count
                break
        
        await db[COLLECTIONS["stores"]].update_one(
            {"id": store_id},
            {"$set": {"menu": menu, "updated_at": datetime.utcnow()}}
        )


# ==================== ORDER ENDPOINTS ====================

@app.get("/api/orders")
async def get_orders(
    user_id: Optional[str] = None,
    store_id: Optional[int] = None,
    status: Optional[str] = None
):
    """Get all orders with optional filters"""
    db = get_database()
    
    query = {}
    if user_id:
        query["user_id"] = user_id
    if store_id:
        query["items.store_id"] = store_id
    if status:
        query["status"] = status
    
    orders_cursor = db[COLLECTIONS["orders"]].find(query).sort("created_at", -1)
    orders = await orders_cursor.to_list(length=100)
    
    result = [schemas.order_helper(order) for order in orders]
    return {"success": True, "data": result}


@app.post("/api/orders")
async def create_order(order_data: models.OrderCreate):
    """Create a new order"""
    db = get_database()
    
    # Calculate total amount
    total_amount = sum(item.price * item.quantity for item in order_data.items)
    
    # Generate order ID
    order_id = f"ORD-{int(datetime.utcnow().timestamp() * 1000)}"
    
    # Create order document
    order_dict = {
        "order_id": order_id,
        "user_id": order_data.user_id,
        "user_name": order_data.user_name,
        "items": [item.dict() for item in order_data.items],
        "total_amount": total_amount,
        "status": "pending",
        "delivery_address": order_data.delivery_address.dict(),
        "payment_method": order_data.payment_method,
        "notes": order_data.notes,
        "timeline": [{
            "status": "pending",
            "timestamp": datetime.utcnow(),
            "note": "Order placed"
        }],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db[COLLECTIONS["orders"]].insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    
    return {
        "success": True,
        "message": "Order created successfully",
        "data": schemas.order_helper(order_dict)
    }


@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: str, status_data: dict):
    """Update order status"""
    db = get_database()
    
    new_status = status_data.get("status")
    if new_status not in ["pending", "preparing", "ready", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Get order
    order = await db[COLLECTIONS["orders"]].find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Add to timeline
    timeline = order.get("timeline", [])
    timeline.append({
        "status": new_status,
        "timestamp": datetime.utcnow(),
        "note": status_data.get("note", f"Order {new_status}")
    })
    
    # Update order
    await db[COLLECTIONS["orders"]].update_one(
        {"order_id": order_id},
        {
            "$set": {
                "status": new_status,
                "timeline": timeline,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"success": True, "message": "Order status updated successfully"}


# ==================== ACTIVE USER ENDPOINTS ====================

@app.get("/api/active-users/count")
async def get_active_user_count():
    """Get total active users (last 5 minutes)"""
    db = get_database()
    
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    count = await db[COLLECTIONS["active_users"]].count_documents({
        "last_activity": {"$gte": five_min_ago}
    })
    
    return {"success": True, "count": count}


@app.get("/api/active-users/ordering-count")
async def get_ordering_user_count():
    """Get users currently ordering"""
    db = get_database()
    
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    count = await db[COLLECTIONS["active_users"]].count_documents({
        "is_ordering": True,
        "last_activity": {"$gte": five_min_ago}
    })
    
    return {"success": True, "count": count}


@app.get("/api/active-users/hunger-level")
async def get_hunger_level():
    """Calculate campus hunger level"""
    db = get_database()
    
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    
    # Get active users
    active_users = await db[COLLECTIONS["active_users"]].count_documents({
        "last_activity": {"$gte": five_min_ago}
    })
    
    ordering_users = await db[COLLECTIONS["active_users"]].count_documents({
        "is_ordering": True,
        "last_activity": {"$gte": five_min_ago}
    })
    
    # Calculate hunger level (0-100)
    # Base on active users and time of day
    current_hour = datetime.utcnow().hour
    
    # Peak hours: 11-14 and 18-21
    is_peak = (11 <= current_hour <= 14) or (18 <= current_hour <= 21)
    
    base_hunger = min((active_users / 100) * 100, 100)  # Scale to 100
    if is_peak:
        base_hunger = min(base_hunger * 1.5, 100)
    
    hunger_level = int(base_hunger)
    
    return {
        "success": True,
        "data": {
            "hunger_level": hunger_level,
            "active_users": active_users,
            "ordering_users": ordering_users
        }
    }


@app.get("/api/active-users/stats")
async def get_active_user_stats():
    """Get comprehensive active user statistics"""
    db = get_database()
    
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    
    # Get all active users
    active_users_cursor = db[COLLECTIONS["active_users"]].find({
        "last_activity": {"$gte": five_min_ago}
    })
    active_users_list = await active_users_cursor.to_list(length=1000)
    
    # Count by store
    by_store = {}
    by_device = {}
    ordering_count = 0
    
    for user in active_users_list:
        if user.get("is_ordering"):
            ordering_count += 1
        
        store = user.get("current_store")
        if store:
            by_store[store] = by_store.get(store, 0) + 1
        
        device = user.get("device_info", {}).get("type", "unknown")
        by_device[device] = by_device.get(device, 0) + 1
    
    # Calculate hunger level
    current_hour = datetime.utcnow().hour
    is_peak = (11 <= current_hour <= 14) or (18 <= current_hour <= 21)
    base_hunger = min((len(active_users_list) / 100) * 100, 100)
    if is_peak:
        base_hunger = min(base_hunger * 1.5, 100)
    hunger_level = int(base_hunger)
    
    # Format device data
    device_list = [{"_id": k, "count": v} for k, v in by_device.items()]
    
    return {
        "success": True,
        "data": {
            "active_users": len(active_users_list),
            "ordering_users": ordering_count,
            "hunger_level": hunger_level,
            "by_store": by_store,
            "by_device": device_list,
            "timestamp": datetime.utcnow()
        }
    }


@app.post("/api/active-users")
async def add_active_user(user_data: models.ActiveUserCreate):
    """Add or update active user"""
    db = get_database()
    
    user_dict = {
        "user_id": user_data.user_id,
        "session_id": user_data.session_id,
        "timestamp": datetime.utcnow(),
        "is_ordering": user_data.is_ordering,
        "current_store": user_data.current_store,
        "device_info": user_data.device_info.dict() if user_data.device_info else {},
        "last_activity": datetime.utcnow()
    }
    
    # Upsert (update if exists, insert if not)
    await db[COLLECTIONS["active_users"]].update_one(
        {"user_id": user_data.user_id},
        {"$set": user_dict},
        upsert=True
    )
    
    return {"success": True, "message": "Active user updated"}


@app.put("/api/active-users/{user_id}/activity")
async def update_user_activity(user_id: str, activity_data: dict):
    """Update user activity"""
    db = get_database()
    
    update_dict = {
        "last_activity": datetime.utcnow(),
        **activity_data
    }
    
    result = await db[COLLECTIONS["active_users"]].update_one(
        {"user_id": user_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Activity updated"}


@app.delete("/api/active-users/{user_id}")
async def remove_active_user(user_id: str):
    """Remove active user"""
    db = get_database()
    
    await db[COLLECTIONS["active_users"]].delete_one({"user_id": user_id})
    
    return {"success": True, "message": "User removed"}


# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/admin/registrations")
async def get_store_registrations():
    """Get all store registration requests"""
    db = get_database()
    
    registrations_cursor = db[COLLECTIONS["store_registrations"]].find().sort("created_at", -1)
    registrations = await registrations_cursor.to_list(length=100)
    
    result = []
    for reg in registrations:
        reg["_id"] = str(reg["_id"])
        result.append(reg)
    
    return {"success": True, "data": result}


@app.post("/api/admin/stores")
async def create_store_by_admin(store_data: models.StoreCreate):
    """Admin creates a new store"""
    db = get_database()
    
    # Check if store already exists
    existing_store = await db[COLLECTIONS["stores"]].find_one({
        "$or": [
            {"email": store_data.email},
            {"store_id": store_data.store_id},
            {"name": store_data.name}
        ]
    })
    
    if existing_store:
        raise HTTPException(
            status_code=400,
            detail="Store with this name, email, or store ID already exists"
        )
    
    # Get next store ID
    last_store = await db[COLLECTIONS["stores"]].find_one(
        {},
        sort=[("id", -1)]
    )
    next_id = (last_store.get("id", 0) + 1) if last_store else 1
    
    # Create store document
    store_dict = {
        "id": next_id,
        "name": store_data.name,
        "store_id": store_data.store_id,
        "email": store_data.email,
        "phone": store_data.phone,
        "hashed_password": hash_password(store_data.password),
        "image": store_data.image,
        "rating": store_data.rating,
        "tagline": store_data.tagline,
        "gradient": store_data.gradient,
        "is_open": store_data.is_open,
        "reviews": store_data.reviews,
        "menu": [],
        "stats": {
            "total_orders": 0,
            "total_revenue": 0,
            "average_rating": store_data.rating
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db[COLLECTIONS["stores"]].insert_one(store_dict)
    store_dict["_id"] = str(result.inserted_id)
    
    return {
        "success": True,
        "message": "Store created successfully",
        "data": schemas.store_helper(store_dict)
    }


# ==================== RATING ENDPOINTS ====================

@app.post("/api/stores/{store_id}/menu/{item_id}/rate")
async def rate_menu_item(store_id: int, item_id: int, rating_data: models.RatingRequest):
    """Rate a menu item (legacy endpoint, use reviews instead)"""
    db = get_database()
    
    # Find store
    store = await db[COLLECTIONS["stores"]].find_one({"id": store_id})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Update menu item
    menu = store.get("menu", [])
    item_found = False
    
    for item in menu:
        if item.get("id") == item_id:
            # Simple average calculation
            old_rating = item.get("rating", 4.0)
            old_count = item.get("review_count", 0)
            
            new_count = old_count + 1
            new_rating = ((old_rating * old_count) + rating_data.rating) / new_count
            
            item["rating"] = round(new_rating, 1)
            item["review_count"] = new_count
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Save updated menu
    await db[COLLECTIONS["stores"]].update_one(
        {"id": store_id},
        {"$set": {"menu": menu, "updated_at": datetime.utcnow()}}
    )
    
    return {
        "success": True,
        "message": "Rating submitted successfully",
        "new_rating": item["rating"],
        "review_count": item["review_count"]
    }


# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

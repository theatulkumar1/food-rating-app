"""
Database Schemas for MongoDB Collections
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


def store_helper(store: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB store document to dict"""
    return {
        "id": store.get("_id"),
        "name": store.get("name"),
        "store_id": store.get("store_id"),
        "email": store.get("email"),
        "phone": store.get("phone"),
        "image": store.get("image"),
        "rating": store.get("rating", 4.0),
        "tagline": store.get("tagline"),
        "gradient": store.get("gradient"),
        "is_open": store.get("is_open", True),
        "reviews": store.get("reviews", 0),
        "menu": store.get("menu", []),
        "stats": store.get("stats", {
            "total_orders": 0,
            "total_revenue": 0,
            "average_rating": 4.0
        }),
        "created_at": store.get("created_at"),
        "updated_at": store.get("updated_at")
    }


def review_helper(review: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB review document to dict"""
    return {
        "id": str(review.get("_id")),
        "store_id": review.get("store_id"),
        "store_name": review.get("store_name"),
        "item_id": review.get("item_id"),
        "item_name": review.get("item_name"),
        "rating": review.get("rating"),
        "comment": review.get("comment"),
        "user_name": review.get("user_name"),
        "user_avatar": review.get("user_avatar", "👤"),
        "status": review.get("status", "approved"),
        "created_at": review.get("created_at"),
        "updated_at": review.get("updated_at")
    }


def order_helper(order: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB order document to dict"""
    return {
        "id": str(order.get("_id")),
        "order_id": order.get("order_id"),
        "user_id": order.get("user_id"),
        "user_name": order.get("user_name"),
        "items": order.get("items", []),
        "total_amount": order.get("total_amount"),
        "status": order.get("status", "pending"),
        "delivery_address": order.get("delivery_address"),
        "payment_method": order.get("payment_method"),
        "notes": order.get("notes"),
        "timeline": order.get("timeline", []),
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at")
    }


def active_user_helper(user: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB active user document to dict"""
    return {
        "id": str(user.get("_id")),
        "user_id": user.get("user_id"),
        "session_id": user.get("session_id"),
        "timestamp": user.get("timestamp"),
        "is_ordering": user.get("is_ordering", False),
        "current_store": user.get("current_store"),
        "device_info": user.get("device_info"),
        "last_activity": user.get("last_activity")
    }


def user_helper(user: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert MongoDB user document to dict"""
    return {
        "id": str(user.get("_id")),
        "username": user.get("username"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "is_admin": user.get("is_admin", False),
        "created_at": user.get("created_at")
    }

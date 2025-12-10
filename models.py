"""
Pydantic Models and Schemas for Campus Food Backend
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# ==================== MENU ITEM MODELS ====================

class MenuItemBase(BaseModel):
    name: str
    price: float
    is_popular: bool = False
    is_favorite: bool = False
    rating: float = 4.0
    review_count: int = 0
    category: Optional[str] = "Fast Food"
    image: Optional[str] = None
    description: Optional[str] = None
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    is_popular: Optional[bool] = None
    is_favorite: Optional[bool] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None


class MenuItem(MenuItemBase):
    id: int
    store_id: int

    class Config:
        from_attributes = True


# ==================== STORE MODELS ====================

class StoreBase(BaseModel):
    name: str
    store_id: str
    email: EmailStr
    phone: str
    image: Optional[str] = None
    rating: float = 4.0
    tagline: Optional[str] = None
    gradient: Optional[str] = None
    reviews: int = 0
    is_open: bool = True


class StoreCreate(StoreBase):
    password: str


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    image: Optional[str] = None
    tagline: Optional[str] = None
    gradient: Optional[str] = None
    is_open: Optional[bool] = None


class Store(StoreBase):
    id: int
    menu: List[MenuItem] = []

    class Config:
        from_attributes = True


# ==================== USER MODELS ====================

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_admin: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    is_admin: bool = False
    store_name: Optional[str] = None
    message: Optional[str] = None


# ==================== STORE REGISTRATION MODELS ====================

class StoreRegistrationBase(BaseModel):
    store_name: str
    store_id: str
    email: EmailStr
    phone: str


class StoreRegistrationCreate(StoreRegistrationBase):
    password: str
    confirm_password: str


class StoreRegistrationResponse(StoreRegistrationBase):
    id: int
    status: str = "pending"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== REVIEW MODELS ====================

class ReviewBase(BaseModel):
    store_id: int
    store_name: str
    item_id: int
    item_name: str
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    user_name: str
    user_avatar: str = "👤"


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    status: Optional[ReviewStatus] = None


class Review(ReviewBase):
    id: str = Field(alias="_id")
    status: ReviewStatus = ReviewStatus.approved
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# ==================== ORDER MODELS ====================

class OrderItem(BaseModel):
    store_id: int
    store_name: str
    item_id: int
    item_name: str
    price: float
    quantity: int


class DeliveryAddress(BaseModel):
    building: str
    room: str
    phone: str


class OrderBase(BaseModel):
    user_id: str
    user_name: str
    items: List[OrderItem]
    delivery_address: DeliveryAddress
    payment_method: str = "cash"
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class TimelineEntry(BaseModel):
    status: OrderStatus
    timestamp: datetime
    note: Optional[str] = None


class Order(OrderBase):
    id: str = Field(alias="_id")
    order_id: str
    total_amount: float
    status: OrderStatus = OrderStatus.pending
    timeline: List[TimelineEntry] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# ==================== ACTIVE USER MODELS ====================

class DeviceInfo(BaseModel):
    type: str = "mobile"  # mobile, desktop, tablet
    os: Optional[str] = None
    browser: Optional[str] = None


class ActiveUserBase(BaseModel):
    user_id: str
    session_id: str
    is_ordering: bool = False
    current_store: Optional[str] = None
    device_info: Optional[DeviceInfo] = None


class ActiveUserCreate(ActiveUserBase):
    pass


class ActiveUser(ActiveUserBase):
    id: str = Field(alias="_id")
    timestamp: datetime
    last_activity: datetime

    class Config:
        populate_by_name = True


# ==================== RATING MODELS ====================

class RatingRequest(BaseModel):
    rating: float = Field(..., ge=1, le=5)


# ==================== STATS MODELS ====================

class ReviewStats(BaseModel):
    rating: float
    count: int


class HungerLevelResponse(BaseModel):
    hunger_level: int
    active_users: int
    ordering_users: int


class ActiveUserStats(BaseModel):
    active_users: int
    ordering_users: int
    hunger_level: int
    by_store: dict
    by_device: List[dict]
    timestamp: datetime

# Campus Food Backend API - Python/FastAPI

Backend server for the Campus Food application using **Python**, **FastAPI**, and **MongoDB**.

## 🚀 Features

- **FastAPI Framework** - Modern, fast (high-performance) Python web framework
- **MongoDB Integration** with Motor (async driver)
- **32+ API Endpoints** - Complete RESTful API
- **Review & Rating System** - Full CRUD operations with auto-calculations
- **Order Management** - Track orders with status timeline
- **Active User Tracking** - Real-time hunger meter calculation
- **Authentication** - Admin, Store, and User login system
- **Password Hashing** - Secure bcrypt password encryption
- **CORS Enabled** - Cross-origin resource sharing configured
- **Async Operations** - Fully asynchronous for better performance

## 📋 Prerequisites

Before running the backend, ensure you have:

- **Python** (v3.8 or higher)
- **pip** (Python package manager)
- **MongoDB** (local installation OR MongoDB Atlas account)

## 🔧 Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Edit `.env` file:

```env
PORT=8000
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=campus_food
FRONTEND_URL=http://localhost:5173
```

### 3. MongoDB Setup

#### Option A: Local MongoDB (Windows)

1. **Download MongoDB**: https://www.mongodb.com/try/download/community
2. **Install MongoDB** with default settings
3. **Start MongoDB Service**:
   ```bash
   net start MongoDB
   ```
4. **Verify Connection**:
   ```bash
   mongosh
   # Should connect to mongodb://localhost:27017
   ```

#### Option B: MongoDB Atlas (Cloud - Recommended)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster (free tier available)
3. Create database user (Database Access)
4. Whitelist IP address (Network Access → Add IP → 0.0.0.0/0 for development)
5. Get connection string (Connect → Connect your application → Python)
6. Update `.env`:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=campus_food
   ```

### 4. Initialize Database

Populate the database with initial data (6 stores, users, reviews):

```bash
python init_db.py
```

This will create:
- 6 food stores with menu items
- Admin user (admin / admin123)
- 2 test users (john_doe / user123)
- 4 sample reviews
- All necessary indexes

## ▶️ Running the Server

### Development Mode (with auto-reload)

```bash
python -m uvicorn main:app --reload --port 8000
```

Or:

```bash
uvicorn main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

**Health Check**: http://localhost:8000/health  
**API Docs**: http://localhost:8000/docs (Swagger UI)  
**Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check

```http
GET /health
```

Returns server status and MongoDB connection status.

---

## Authentication API

### Login
```http
POST /api/auth/login
```

**Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "is_admin": true,
  "message": "Admin login successful"
}
```

### Register User
```http
POST /api/auth/register-user
```

**Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "phone": "+1234567890",
  "password": "password123"
}
```

### Register Store
```http
POST /api/auth/register-store
```

**Body:**
```json
{
  "store_name": "NEW STORE",
  "store_id": "newstore",
  "email": "store@campus.com",
  "phone": "+1234567890",
  "password": "store123",
  "confirm_password": "store123"
}
```

---

## Store API

### Get All Stores
```http
GET /api/stores
GET /api/stores?open=true
```

### Get Store by ID
```http
GET /api/stores/{store_id}
```

### Get Store by Name
```http
GET /api/stores/by-name/{store_name}
```

**Example:** `GET /api/stores/by-name/GREEN CHILLIES`

### Update Store Status
```http
PATCH /api/stores/{store_id}/status?is_open=true
```

---

## Menu API

### Get Store Menu
```http
GET /api/stores/{store_id}/menu
```

### Update Entire Menu
```http
PUT /api/stores/{store_id}/menu
```

**Body:**
```json
[
  {
    "id": 1,
    "name": "Pizza",
    "price": 250,
    "is_popular": true,
    "rating": 4.5,
    "review_count": 42
  }
]
```

### Update Menu Item
```http
PUT /api/stores/{store_id}/menu/{item_id}
```

---

## Review API

### Get All Reviews
```http
GET /api/reviews
GET /api/reviews?store_id=1
GET /api/reviews?item_id=1
GET /api/reviews?user_name=john_doe
```

### Get Store Reviews
```http
GET /api/reviews/store/{store_id}
```

### Get Item Reviews
```http
GET /api/reviews/store/{store_id}/item/{item_id}
```

**Example:** `GET /api/reviews/store/1/item/1`

### Create Review
```http
POST /api/reviews
```

**Body:**
```json
{
  "store_id": 1,
  "store_name": "GREEN CHILLIES",
  "item_id": 1,
  "item_name": "Spicy Chicken Burger",
  "rating": 5,
  "comment": "Absolutely delicious!",
  "user_name": "john_doe",
  "user_avatar": "👨"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Review submitted successfully",
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "store_id": 1,
    "rating": 5,
    "comment": "Absolutely delicious!",
    "created_at": "2024-01-15T10:30:45.123Z"
  }
}
```

### Get Review Stats
```http
GET /api/reviews/stats/{store_id}/{item_id}
```

**Example:** `GET /api/reviews/stats/1/1`

**Response:**
```json
{
  "success": true,
  "data": {
    "rating": 4.7,
    "count": 42
  }
}
```

---

## Order API

### Get All Orders
```http
GET /api/orders
GET /api/orders?user_id=john_doe
GET /api/orders?store_id=1
GET /api/orders?status=pending
```

### Create Order
```http
POST /api/orders
```

**Body:**
```json
{
  "user_id": "john_doe",
  "user_name": "John Doe",
  "items": [
    {
      "store_id": 1,
      "store_name": "GREEN CHILLIES",
      "item_id": 1,
      "item_name": "Spicy Chicken Burger",
      "price": 120,
      "quantity": 2
    }
  ],
  "delivery_address": {
    "building": "Hostel A",
    "room": "201",
    "phone": "+91 9876543210"
  },
  "payment_method": "cash",
  "notes": "Extra spicy please"
}
```

### Update Order Status
```http
PUT /api/orders/{order_id}/status
```

**Body:**
```json
{
  "status": "preparing",
  "note": "Chef is preparing your order"
}
```

**Valid statuses:** pending, preparing, ready, delivered, cancelled

---

## Active Users API

### Get Active User Count
```http
GET /api/active-users/count
```

**Response:**
```json
{
  "success": true,
  "count": 95
}
```

### Get Ordering User Count
```http
GET /api/active-users/ordering-count
```

### Get Hunger Level
```http
GET /api/active-users/hunger-level
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hunger_level": 85,
    "active_users": 95,
    "ordering_users": 48
  }
}
```

### Get Active User Stats
```http
GET /api/active-users/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_users": 95,
    "ordering_users": 48,
    "hunger_level": 85,
    "by_store": {
      "GREEN CHILLIES": 15,
      "NESCAFE": 8
    },
    "by_device": [
      {"_id": "mobile", "count": 75},
      {"_id": "desktop", "count": 20}
    ],
    "timestamp": "2024-01-15T10:30:45.123Z"
  }
}
```

### Add/Update Active User
```http
POST /api/active-users
```

**Body:**
```json
{
  "user_id": "user123",
  "session_id": "session_xyz",
  "is_ordering": true,
  "current_store": "GREEN CHILLIES",
  "device_info": {
    "type": "mobile",
    "os": "iOS"
  }
}
```

### Update User Activity
```http
PUT /api/active-users/{user_id}/activity
```

**Body:**
```json
{
  "is_ordering": true,
  "current_store": "NESCAFE"
}
```

### Remove Active User
```http
DELETE /api/active-users/{user_id}
```

---

## Admin API

### Get Store Registrations
```http
GET /api/admin/registrations
```

### Create Store (Admin)
```http
POST /api/admin/stores
```

**Body:**
```json
{
  "name": "NEW STORE",
  "store_id": "newstore",
  "email": "store@campus.com",
  "phone": "+1234567890",
  "password": "store123",
  "image": "https://images.unsplash.com/...",
  "rating": 4.0,
  "tagline": "Fresh Food",
  "gradient": "from-blue-500 to-purple-500",
  "is_open": true,
  "reviews": 0
}
```

---

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get all stores
curl http://localhost:8000/api/stores

# Get reviews for item
curl http://localhost:8000/api/reviews/store/1/item/1

# Create review
curl -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{"store_id":1,"store_name":"GREEN CHILLIES","item_id":1,"item_name":"Burger","rating":5,"comment":"Great!","user_name":"john"}'
```

### Using FastAPI Swagger UI

1. Start the server
2. Open http://localhost:8000/docs
3. Interactive API documentation with "Try it out" feature

### Using Python Requests

```python
import requests

# Get all stores
response = requests.get("http://localhost:8000/api/stores")
stores = response.json()

# Create review
review_data = {
    "store_id": 1,
    "store_name": "GREEN CHILLIES",
    "item_id": 1,
    "item_name": "Burger",
    "rating": 5,
    "comment": "Delicious!",
    "user_name": "john_doe"
}
response = requests.post("http://localhost:8000/api/reviews", json=review_data)
```

---

## 📊 MongoDB Collections

### stores
```javascript
{
  "_id": ObjectId,
  "id": 1,
  "name": "GREEN CHILLIES",
  "store_id": "greenchillies",
  "email": "greenchillies@campus.com",
  "phone": "+1234567890",
  "hashed_password": "...",
  "image": "https://...",
  "rating": 4.5,
  "tagline": "...",
  "gradient": "...",
  "is_open": true,
  "reviews": 245,
  "menu": [
    {
      "id": 1,
      "name": "Spicy Chicken Burger",
      "price": 120,
      "is_popular": true,
      "rating": 4.6,
      "review_count": 45
    }
  ],
  "stats": {
    "total_orders": 0,
    "total_revenue": 0,
    "average_rating": 4.5
  },
  "created_at": "2024-01-15T...",
  "updated_at": "2024-01-15T..."
}
```

### reviews
```javascript
{
  "_id": ObjectId,
  "store_id": 1,
  "store_name": "GREEN CHILLIES",
  "item_id": 1,
  "item_name": "Spicy Chicken Burger",
  "rating": 5,
  "comment": "Absolutely delicious!",
  "user_name": "john_doe",
  "user_avatar": "👨",
  "status": "approved",
  "created_at": "2024-01-15T...",
  "updated_at": "2024-01-15T..."
}
```

### users
```javascript
{
  "_id": ObjectId,
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "hashed_password": "...",
  "is_admin": false,
  "created_at": "2024-01-15T..."
}
```

### orders
```javascript
{
  "_id": ObjectId,
  "order_id": "ORD-1705315845123",
  "user_id": "john_doe",
  "user_name": "John Doe",
  "items": [...],
  "total_amount": 240,
  "status": "pending",
  "delivery_address": {...},
  "payment_method": "cash",
  "timeline": [
    {
      "status": "pending",
      "timestamp": "2024-01-15T...",
      "note": "Order placed"
    }
  ],
  "created_at": "2024-01-15T...",
  "updated_at": "2024-01-15T..."
}
```

### active_users
```javascript
{
  "_id": ObjectId,
  "user_id": "user123",
  "session_id": "session_xyz",
  "timestamp": "2024-01-15T...",
  "is_ordering": true,
  "current_store": "GREEN CHILLIES",
  "device_info": {
    "type": "mobile",
    "os": "iOS"
  },
  "last_activity": "2024-01-15T..."
}
```

---

## 🛠️ Troubleshooting

### MongoDB Connection Issues

**Error:** `ServerSelectionTimeoutError`

**Solutions:**
1. Check if MongoDB is running:
   ```bash
   # Windows
   net start MongoDB
   
   # Check service status
   sc query MongoDB
   ```

2. Verify connection URI in `.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   ```

3. For Atlas:
   - Check IP whitelist (Network Access)
   - Verify username/password
   - Ensure database user has read/write permissions

### Port Already in Use

**Error:** `Address already in use`

**Solutions:**

```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or change port in .env or command
uvicorn main:app --reload --port 8001
```

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install fastapi motor passlib
```

### Database Empty

**Solution:**

```bash
# Run initialization script
python init_db.py
```

---

## 🚀 Deployment

### Deploying to Heroku

```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Set environment variables
heroku config:set MONGODB_URI=your_atlas_uri
heroku config:set DATABASE_NAME=campus_food
heroku config:set FRONTEND_URL=https://your-frontend.vercel.app

# Initialize database
heroku run python init_db.py
```

### Deploying to Railway/Render

1. Connect GitHub repository
2. Set root directory to `/backend`
3. Add environment variables
4. Deploy command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Environment Variables for Production

```env
PORT=8000
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=campus_food
FRONTEND_URL=https://your-frontend-domain.com
ENV=production
```

---

## 📝 Development Notes

- **All timestamps** are stored in UTC
- **Review status** defaults to 'approved' (implement moderation as needed)
- **Order IDs** format: ORD-{timestamp in milliseconds}
- **Passwords** are hashed using bcrypt
- **Active users** should be cleaned up periodically (implement TTL or cleanup job)
- **Hunger level** calculation: based on active users and time of day (peak: 11am-2pm, 6pm-9pm)

---

## 📦 Project Structure

```
backend/
├── main.py                    # Main FastAPI application
├── database.py                # MongoDB connection setup
├── models.py                  # Pydantic models for validation
├── schemas.py                 # Helper functions for data conversion
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── .env                       # Your credentials (create this)
└── README.md                  # This file
```

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

**Made with ❤️ for Campus Food Students** 🍕

**Backend Stack:** Python • FastAPI • MongoDB • Motor • Pydantic 🚀

# -------------------- IMPORTS --------------------
import os
import bcrypt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# -------------------- APP INIT --------------------
app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE CONNECTION --------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set")

try:
    client = MongoClient(MONGO_URI)
    db = client.get_database()  # Uses DB from URI (aura_crypt)
    users_collection = db["users"]
    print("✅ Connected to MongoDB successfully")
except ConnectionFailure:
    raise Exception("❌ Could not connect to MongoDB")

# -------------------- MODELS --------------------
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# -------------------- ROUTES --------------------

@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


# -------- REGISTER --------
@app.post("/register")
def register(user: UserRegister):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    )

    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    })

    return {"message": "User registered successfully ✅"}


# -------- LOGIN --------
@app.post("/login")
def login(user: UserLogin):
    existing_user = users_collection.find_one({"email": user.email})

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not bcrypt.checkpw(
        user.password.encode("utf-8"),
        existing_user["password"]
    ):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful ✅"}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from pymongo import MongoClient
import os

# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI()

# Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Database Setup
# -----------------------------
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise Exception("MONGO_URL not set in environment variables")

client = MongoClient(MONGO_URL)
db = client["aura_crypt"]
users_collection = db["users"]

# -----------------------------
# Password Hashing
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# Models
# -----------------------------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# -----------------------------
# Routes
# -----------------------------

@app.get("/")
def root():
    return {"message": "Aura Crypt API is running successfully 🚀"}

@app.post("/register")
def register(user: UserRegister):
    # Check if email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    })

    return {
        "status": "success",
        "message": "User registered successfully"
    }

@app.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {
        "status": "success",
        "message": "Login successful"
    }

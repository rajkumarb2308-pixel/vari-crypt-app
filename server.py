from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from pymongo import MongoClient, errors
import os

# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Password Hashing
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# Database Connection (Safe)
# -----------------------------
MONGO_URL = "mongodb+srv://rajkumarb2308_db_user:NEW_PASSWORD@aura-crypt.innejxe.mongodb.net/aura_crypt?retryWrites=true&w=majority"

if not MONGO_URL:
    raise Exception("MONGO_URL environment variable not set")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    
    # Force connection test
    client.admin.command("ping")
    
    # IMPORTANT: Get database from URI itself
    db = client.get_default_database()
    users_collection = db["users"]

    print("✅ MongoDB Connected Successfully")

except errors.ServerSelectionTimeoutError as e:
    raise Exception(f"MongoDB connection failed: {e}")

except errors.OperationFailure as e:
    raise Exception(f"MongoDB authentication failed: {e}")

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
    return {"message": "Aura Crypt API running 🚀"}

@app.post("/register")
def register(user: UserRegister):
    try:
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
def login(user: UserLogin):
    try:
        db_user = users_collection.find_one({"email": user.email})

        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        if not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        return {
            "status": "success",
            "message": "Login successful"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






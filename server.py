from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from pymongo import MongoClient
import os

app = FastAPI()

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Password Hashing ------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------ MongoDB Connection ------------------
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise Exception("MONGO_URL not set")

try:
    client = MongoClient(MONGO_URL, tls=True)
    
    # Force connection check
    client.admin.command("ping")
    
    # Explicit DB selection
    db = client["aura_crypt"]
    users_collection = db["users"]

    print("✅ MongoDB Connected")

except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    raise e

# ------------------ Models ------------------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ------------------ Routes ------------------
@app.get("/")
def root():
    return {"message": "API Running Successfully 🚀"}


@app.post("/register")
def register(user: UserRegister):
    existing = users_collection.find_one({"email": user.email})
    if existing:
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

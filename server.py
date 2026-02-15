import os
import bcrypt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set")

try:
    client = MongoClient(MONGO_URI)
    db = client["aura_crypt"]   # 🔥 Force DB explicitly
    users_collection = db["users"]
    print("✅ MongoDB Connected")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
    raise e


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/register")
def register(user: UserRegister):
    try:
        if users_collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already exists")

        hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

        users_collection.insert_one({
            "username": user.username,
            "email": user.email,
            "password": hashed_pw
        })

        return {"message": "Registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
def login(user: UserLogin):
    try:
        existing_user = users_collection.find_one({"email": user.email})

        if not existing_user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not bcrypt.checkpw(user.password.encode(), existing_user["password"]):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        return {"message": "Login successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

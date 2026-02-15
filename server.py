# ==========================================
# 🚀 SERVER.PY (FASTAPI BACKEND - PRODUCTION READY)
# ==========================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import bcrypt
import os
import uuid
from datetime import datetime

app = FastAPI()

# ==========================================
# 🌐 CORS CONFIG (SAFE FOR TOKEN-LESS API)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🛢 DATABASE CONNECTION (ENV SAFE)
# ==========================================
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI environment variable not set")

try:
    client = MongoClient(MONGO_URI)
    db = client["vari_crypt_db"]
    users_collection = db["users"]
    messages_collection = db["messages"]
    print("✅ Connected to MongoDB Cloud!")
except Exception as e:
    raise Exception(f"❌ Database connection failed: {e}")

# ==========================================
# 📦 MODELS
# ==========================================
class AuthModel(BaseModel):
    identifier: str
    password: str


# ==========================================
# 🔐 AUTH ROUTES
# ==========================================
@app.post("/register")
def register_user(user: AuthModel):
    existing = users_collection.find_one({"identifier": user.identifier})
    if existing:
        raise HTTPException(status_code=400, detail="IDENTITY ALREADY EXISTS")

    hashed_pw = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")  # store as string

    users_collection.insert_one({
        "identifier": user.identifier,
        "password": hashed_pw,
        "joined_at": datetime.utcnow()
    })

    return {"message": "IDENTITY ESTABLISHED"}


@app.post("/login")
def login_user(creds: AuthModel):
    user = users_collection.find_one({"identifier": creds.identifier})

    if not user:
        raise HTTPException(status_code=401, detail="USER NOT FOUND")

    if not bcrypt.checkpw(
        creds.password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="WRONG PASSWORD")

    return {"user": user["identifier"]}


# ==========================================
# 📡 MESSAGE ROUTES
# ==========================================
@app.post("/send")
def send_data(data: dict):
    try:
        visual_data = data["encrypted_payload"]["visual_data"]
    except KeyError:
        raise HTTPException(status_code=400, detail="INVALID PAYLOAD FORMAT")

    msg_id = str(uuid.uuid4())[:8]

    messages_collection.insert_one({
        "msg_id": msg_id,
        "visual_data": visual_data,
        "createdAt": datetime.utcnow()
    })

    return {"msg_id": msg_id}


@app.get("/receive/{msg_id}")
def receive_data(msg_id: str):
    record = messages_collection.find_one_and_delete({"msg_id": msg_id})

    if not record:
        raise HTTPException(status_code=404, detail="SIGNAL NOT FOUND OR EXPIRED")

    return {"visual_data": record["visual_data"]}


# ==========================================
# 🧪 HEALTH CHECK
# ==========================================
@app.get("/")
def health():
    return {"status": "Vari-Crypt Server is Live (Mode: cloud)"}


# Prevent 405 logs from Render health checks
@app.head("/")
def head_health():
    return {"status": "OK"}

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
# ⚙️ CONFIGURATION
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ DATABASE CONNECTION ⚠️
# For local testing, you can paste your string here.
# For production (Render), use os.getenv("MONGO_URI") to keep it safe.
MONGO_URI = "mongodb+srv://rajkumarb2308_db_user:rgfobjMajgiVhxpd@aura-crypt.innejxe.mongodb.net/?appName=aura-crypt"

try:
    client = MongoClient(MONGO_URI)
    db = client.vari_crypt_db
    users_collection = db.users
    messages_collection = db.messages
    print("✅ CONNECTED TO MONGODB ATLAS: aura-crypt")
except Exception as e:
    print(f"❌ DATABASE CONNECTION FAILED: {e}")


class AuthModel(BaseModel):
    identifier: str
    password: str


# ==========================================
# 🔐 AUTHENTICATION ROUTES
# ==========================================
@app.post("/register")
def register_user(user: AuthModel):
    # Check for duplicates
    if users_collection.find_one({"identifier": user.identifier}):
        raise HTTPException(status_code=400, detail="IDENTITY ALREADY EXISTS.")

    # Hash password
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    users_collection.insert_one({
        "identifier": user.identifier,
        "password": hashed_pw,
        "joined_at": datetime.utcnow()
    })
    return {"message": "IDENTITY ESTABLISHED"}


@app.post("/login")
def login_user(creds: AuthModel):
    user = users_collection.find_one({"identifier": creds.identifier})

    if user and bcrypt.checkpw(creds.password.encode('utf-8'), user['password']):
        return {"user": user["identifier"]}

    raise HTTPException(status_code=401, detail="ACCESS DENIED")


# ==========================================
# 📡 DATA TRANSMISSION ROUTES
# ==========================================
@app.post("/send")
def send_data(data: dict):
    msg_id = str(uuid.uuid4())[:8]

    # Store Encrypted Payload
    messages_collection.insert_one({
        "msg_id": msg_id,
        "visual_data": data['encrypted_payload']['visual_data'],
        "createdAt": datetime.utcnow()
    })

    return {"msg_id": msg_id}


@app.get("/receive/{msg_id}")
def receive_data(msg_id: str):
    # Self-Destruct: Delete immediately after reading
    record = messages_collection.find_one_and_delete({"msg_id": msg_id})

    if not record:
        raise HTTPException(status_code=404, detail="SIGNAL NOT FOUND OR EXPIRED")

    return {"visual_data": record["visual_data"]}

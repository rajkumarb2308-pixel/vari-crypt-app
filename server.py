from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from pymongo import MongoClient

app = FastAPI(title="Vari-Crypt Secure Cloud Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REPLACE THIS with your free MongoDB Atlas URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rajkumarb2308_db_user:rgfobjMajgiVhxpd@aura-crypt.innejxe.mongodb.net/?appName=aura-crypt")

db_mode = "memory"
messages_collection = {}

# Try Cloud DB, Fallback to Local Memory for testing
try:
    if "YOUR_MONGO_URI_HERE" not in MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')  # Test connection
        db = client["varicrypt_db"]
        messages_collection = db["messages"]
        db_mode = "cloud"
        print("✅ Connected to MongoDB Cloud!")
except Exception as e:
    print(f"⚠️ Cloud DB Failed: {e}. Falling back to Local Memory Mode.")


class Message(BaseModel):
    encrypted_payload: dict


@app.get("/")
def home():
    return {"status": f"Vari-Crypt Server is Live (Mode: {db_mode})"}


@app.post("/send")
def send_message(message: Message):
    message_id = str(uuid.uuid4())[:8]
    document = {"message_id": message_id, "payload": message.encrypted_payload}

    if db_mode == "cloud":
        messages_collection.insert_one(document)
    else:
        messages_collection[message_id] = document

    return {"success": True, "message_id": message_id}


@app.get("/receive/{message_id}")
def receive_message(message_id: str):
    if db_mode == "cloud":
        document = messages_collection.find_one({"message_id": message_id})
    else:
        document = messages_collection.get(message_id)

    if not document:
        raise HTTPException(status_code=404, detail="Message not found.")
    return document["payload"]
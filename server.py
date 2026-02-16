from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
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
# For production (Render), it is safer to use os.getenv("MONGO_URI")
MONGO_URI = "mongodb+srv://rajkumarb2308_db_user:NEW_PASSWORD@aura-crypt.innejxe.mongodb.net/aura_crypt?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI)
    db = client.vari_crypt_db
    # We only need the messages collection now
    messages_collection = db.messages
    print("✅ CONNECTED TO MONGODB ATLAS: aura-crypt")
except Exception as e:
    print(f"❌ DATABASE CONNECTION FAILED: {e}")

# ==========================================
# 📡 DATA TRANSMISSION ROUTES
# ==========================================

@app.get("/")
def home():
    return {"status": "Vari-Crypt Server is Running"}

@app.post("/send")
def send_data(data: dict):
    """
    Receives encrypted visual data from app.py and stores it with a unique ID.
    """
    # Generate a short 8-character ID for the user to retrieve data later
    msg_id = str(uuid.uuid4())[:8]

    # Store Encrypted Payload into MongoDB
    try:
        messages_collection.insert_one({
            "msg_id": msg_id,
            # This matches the JSON structure sent from your app.py
            "visual_data": data['encrypted_payload']['visual_data'],
            "createdAt": datetime.utcnow()
        })
        return {"msg_id": msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/receive/{msg_id}")
def receive_data(msg_id: str):
    """
    Retrieves data using the ID and deletes it immediately (One-Time View).
    """
    # Find and delete ensures the data is truly ephemeral (Self-Destruct)
    record = messages_collection.find_one_and_delete({"msg_id": msg_id})

    if not record:
        raise HTTPException(status_code=404, detail="SIGNAL NOT FOUND OR EXPIRED")

    return {"visual_data": record["visual_data"]}

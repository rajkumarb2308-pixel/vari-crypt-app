from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import uuid
import os
from datetime import datetime

app = FastAPI()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['vari_crypt_db']
collection = db['messages']


def generate_id():
    return str(uuid.uuid4())[:8]


@app.post("/send")
async def send_data(payload: dict):
    try:
        msg_id = generate_id()
        visual_data = payload["encrypted_payload"]["visual_data"]

        # This record now includes the 'createdAt' field for auto-deletion
        new_record = {
            "msg_id": msg_id,
            "visual_data": visual_data,
            "createdAt": datetime.utcnow()  # REQUIRED for TTL index
        }

        collection.insert_one(new_record)
        return {"msg_id": msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/receive/{msg_id}")
async def receive_data(msg_id: str):
    # Single-Use Logic: Finds and DELETES immediately upon extraction
    record = collection.find_one_and_delete({"msg_id": msg_id})

    if record:
        return {"visual_data": record["visual_data"]}
    else:
        raise HTTPException(status_code=404, detail="Signal lost: Data extracted or expired.")


@app.get("/")
def health_check():
    return {"status": "Active", "mode": "Cloud"}

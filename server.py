# ==========================================
# 🚀 VARI-CRYPT SERVER V2 (JWT + TTL READY)
# ==========================================

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
import uuid

# =============================
# 🔐 CONFIG
# =============================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set")

client = MongoClient(MONGO_URI)
db = client["vari_crypt_db"]
users_collection = db["users"]
messages_collection = db["messages"]

# Create TTL index (1 hour expiry)
messages_collection.create_index(
    [("createdAt", ASCENDING)],
    expireAfterSeconds=3600
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# 📦 MODELS
# =============================
class AuthModel(BaseModel):
    identifier: str
    password: str

class MessageModel(BaseModel):
    visual_data: str


# =============================
# 🔐 JWT UTIL
# =============================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(auth_header: str = Header(None)):
    if not auth_header:
        raise HTTPException(status_code=401, detail="TOKEN REQUIRED")

    try:
        scheme, token = auth_header.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="INVALID TOKEN")


# =============================
# 🔐 AUTH ROUTES
# =============================
@app.post("/register")
def register(user: AuthModel):
    if users_collection.find_one({"identifier": user.identifier}):
        raise HTTPException(status_code=400, detail="IDENTITY EXISTS")

    hashed = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    ).decode()

    users_collection.insert_one({
        "identifier": user.identifier,
        "password": hashed,
        "created_at": datetime.utcnow()
    })

    return {"message": "REGISTERED SUCCESSFULLY"}


@app.post("/login")
def login(user: AuthModel):
    db_user = users_collection.find_one({"identifier": user.identifier})

    if not db_user:
        raise HTTPException(status_code=401, detail="USER NOT FOUND")

    if not bcrypt.checkpw(
        user.password.encode(),
        db_user["password"].encode()
    ):
        raise HTTPException(status_code=401, detail="WRONG PASSWORD")

    token = create_access_token({"sub": user.identifier})

    return {"access_token": token, "token_type": "bearer"}


# =============================
# 📡 PROTECTED MESSAGE ROUTES
# =============================
@app.post("/send")
def send_message(data: MessageModel, user=Depends(verify_token)):

    msg_id = str(uuid.uuid4())[:8]

    messages_collection.insert_one({
        "msg_id": msg_id,
        "visual_data": data.visual_data,
        "owner": user,
        "createdAt": datetime.utcnow()
    })

    return {"msg_id": msg_id}


@app.get("/receive/{msg_id}")
def receive_message(msg_id: str, user=Depends(verify_token)):

    record = messages_collection.find_one_and_delete({
        "msg_id": msg_id,
        "owner": user
    })

    if not record:
        raise HTTPException(status_code=404, detail="NOT FOUND OR EXPIRED")

    return {"visual_data": record["visual_data"]}


@app.get("/")
def health():
    return {"status": "Vari-Crypt Server V2 Running"}

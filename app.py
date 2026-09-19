"""
Palm Pay API — demo backend.

Run locally:
    pip install -r requirements.txt
    uvicorn app:app --reload --port 8000

DEMO ONLY — see biometric.py for why this isn't production-secure.
"""

import base64
import binascii

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from biometric import extract_features, find_best_match
from store import create_user, get_user, charge_user, list_users

app = FastAPI(title="Palm Pay API (Demo)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterRequest(BaseModel):
    name: str
    image_base64: str          # data URL or raw base64 of a captured palm photo
    starting_balance: float = 100.0


class PayRequest(BaseModel):
    image_base64: str
    amount: float
    merchant: str = "Demo Store"


def _decode_image(image_base64: str) -> bytes:
    if "," in image_base64:  # strip data URL prefix like "data:image/png;base64,"
        image_base64 = image_base64.split(",", 1)[1]
    try:
        return base64.b64decode(image_base64)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid image data")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/register")
def register(payload: RegisterRequest):
    image_bytes = _decode_image(payload.image_base64)
    features = extract_features(image_bytes)
    user_id = create_user(payload.name, features, payload.starting_balance)
    return {"user_id": user_id, "name": payload.name, "balance": payload.starting_balance}


@app.post("/pay")
def pay(payload: PayRequest):
    image_bytes = _decode_image(payload.image_base64)
    features = extract_features(image_bytes)

    from store import USERS
    match = find_best_match(features, USERS)

    if not match:
        raise HTTPException(status_code=401, detail="Palm not recognized. Please register first or try again.")

    try:
        txn = charge_user(match["user_id"], payload.amount, payload.merchant)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    return {
        "status": "success",
        "user": match["name"],
        "match_confidence": match["score"],
        "transaction": txn,
    }


@app.get("/users")
def users():
    """Demo-only endpoint to see enrolled users and balances."""
    return {"users": list_users()}

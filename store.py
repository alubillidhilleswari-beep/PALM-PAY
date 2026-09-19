"""
Simple in-memory store for the demo. Replace with a real database
(Postgres, etc.) before this goes anywhere near production — and never
store raw palm images or reversible biometric data long-term; store
only irreversible templates, encrypted at rest.
"""

import uuid

# user_id -> {name, palm_features, balance}
USERS: dict = {}

# list of {id, user_id, amount, merchant, timestamp}
TRANSACTIONS: list = []


def create_user(name: str, palm_features: list, starting_balance: float = 100.0) -> str:
    user_id = str(uuid.uuid4())[:8]
    USERS[user_id] = {
        "name": name,
        "palm_features": palm_features,
        "balance": starting_balance,
    }
    return user_id


def get_user(user_id: str) -> dict | None:
    return USERS.get(user_id)


def charge_user(user_id: str, amount: float, merchant: str) -> dict:
    user = USERS[user_id]
    if user["balance"] < amount:
        raise ValueError("Insufficient balance")

    user["balance"] -= amount

    txn = {
        "id": str(uuid.uuid4())[:8],
        "user_id": user_id,
        "amount": amount,
        "merchant": merchant,
        "balance_after": user["balance"],
    }
    TRANSACTIONS.append(txn)
    return txn


def list_users() -> list:
    return [{"user_id": uid, "name": r["name"], "balance": r["balance"]} for uid, r in USERS.items()]

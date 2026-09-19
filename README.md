# 🖐️ Palm Pay (Demo/Prototype)

Palm Pay is a demo web app where users register by capturing a photo
of their palm, then "pay" at a (simulated) merchant by scanning their
palm again — no card, cash, or phone required.

## ⚠️ Important: this is a prototype, not a secure payment system

This project is meant to demonstrate the **user flow and app
structure** of a palm-based payment system. It is **not secure enough
for real money or real biometric identity verification**. Specifically:

- It uses a regular webcam photo + a basic image-histogram comparison
  as a stand-in for real palm biometrics. Real palm-recognition systems
  use near-infrared palm-vein imaging (the vein pattern under your skin,
  which is very hard to spoof) plus a trained deep-learning matcher —
  not a photo of your palm's surface.
- There's no liveness detection, so this demo could be tricked by a
  printed photo — a real system must detect that a live hand is present.
- Palm images/features are stored in memory, unencrypted, for demo
  purposes. A production system must never store raw biometric images,
  should store only irreversible encrypted templates, and must comply
  with biometric privacy law (which varies significantly by country/state).
- Payments here are fully simulated (an in-memory wallet balance) —
  there's no real payment processor, bank connection, or fraud protection.

**Before building this into anything real**, you'd need a real palm-vein
sensor and matching SDK, liveness/anti-spoofing detection, a licensed
payment processor integration, and legal review for biometric data
handling and payments regulation in your jurisdiction.

## Project structure

```
palmpay/
├── backend/
│   ├── app.py          # FastAPI app: /register, /pay, /users
│   ├── biometric.py    # Mock palm "fingerprint" extraction + matching
│   ├── store.py        # In-memory user/wallet/transaction store
│   └── requirements.txt
├── frontend/
│   ├── index.html      # Register / Pay / Users tabs, webcam capture
│   ├── style.css
│   └── script.js
└── README.md
```

## Running it locally

**1. Start the backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**2. Open the frontend**

Open `frontend/index.html` in a browser (or serve it with
`python -m http.server` from inside `frontend/`). Your browser will
ask for camera permission — allow it.

> Camera access only works over `https://` or on `localhost`, so if
> you deploy the frontend elsewhere, make sure it's served over HTTPS.

**3. Try the flow**

1. Go to **Register Palm** — enter your name, set a starting balance,
   click **Capture Palm & Register**.
2. Go to **Pay** — enter an amount, click **Scan Palm & Pay**. It
   compares the new capture against registered palms and, if matched,
   deducts from that user's balance.
3. Check **Enrolled Users** to see current balances.

## API reference

- `POST /register` — `{ name, image_base64, starting_balance }` → creates a user
- `POST /pay` — `{ image_base64, amount, merchant }` → finds matching user, charges them
- `GET /users` — list all enrolled users and balances (demo-only visibility)
- `GET /health` — basic health check

## Extending it

- Replace `biometric.py`'s `extract_features`/`match` with a real
  palm-vein sensor SDK and a trained embedding model.
- Replace `store.py` with a real database and encrypted-at-rest
  biometric templates (never raw images).
- Add liveness detection before accepting a capture as a real hand.
- Integrate a real payment processor instead of the in-memory wallet.

"""
Palm Pay — demo biometric matching module.

IMPORTANT: This is a PROTOTYPE for demonstration purposes only. It uses a
simple image-histogram "fingerprint" as a stand-in for real palm-vein/
palm-print biometric recognition, and is NOT secure enough for real
payments. A production system would need:

  - A proper palm-vein or palm-print sensor (near-infrared imaging),
    not a regular webcam photo
  - A trained deep-learning matcher (e.g. a Siamese/embedding network)
    instead of a basic histogram comparison
  - Liveness detection to prevent spoofing with a photo or printout
  - Encrypted, irreversible biometric templates (never store raw images)
  - Regulatory compliance for biometric data (varies by country) and
    for payments (PCI-DSS, KYC/AML)

Swap the extract_features() and match() functions below for a real
biometric SDK/model when moving beyond a demo.
"""

import io
import math
from typing import Optional

from PIL import Image


def extract_features(image_bytes: bytes) -> list:
    """Turn an image into a simple numeric fingerprint (a color histogram).
    This stands in for a real palm-print/vein embedding vector."""
    img = Image.open(io.BytesIO(image_bytes)).convert("L").resize((64, 64))
    histogram = img.histogram()  # 256 values, 0-255 pixel intensity counts
    total = sum(histogram) or 1
    normalized = [h / total for h in histogram]
    return normalized


def _cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def match(features: list, enrolled_features: list, threshold: float = 0.93) -> tuple[bool, float]:
    """Compare a captured fingerprint against an enrolled one.
    Returns (is_match, similarity_score)."""
    similarity = _cosine_similarity(features, enrolled_features)
    return similarity >= threshold, round(similarity, 4)


def find_best_match(features: list, users: dict, threshold: float = 0.93) -> Optional[dict]:
    """Search all enrolled users for the closest match above threshold."""
    best_user = None
    best_score = 0.0

    for user_id, record in users.items():
        is_match, score = match(features, record["palm_features"], threshold)
        if is_match and score > best_score:
            best_score = score
            best_user = {"user_id": user_id, "name": record["name"], "score": score}

    return best_user

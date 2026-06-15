import base64
import hashlib
import hmac
import secrets
import time
from typing import Optional

from app.core.config import settings

PASSWORD_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    return f"{salt}${base64.b64encode(digest).decode('utf-8')}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, stored_digest = password_hash.split("$", 1)
    except ValueError:
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    candidate_digest = base64.b64encode(candidate).decode("utf-8")
    return hmac.compare_digest(candidate_digest, stored_digest)


def create_access_token(user_id: str) -> str:
    issued_at = str(int(time.time()))
    payload = f"{user_id}:{issued_at}"
    signature = hmac.new(
        settings.AUTH_SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    token_body = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token_body.encode("utf-8")).decode("utf-8")


def decode_access_token(token: str) -> Optional[str]:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id, issued_at, signature = decoded.split(":", 2)
    except Exception:
        return None

    payload = f"{user_id}:{issued_at}"
    expected_signature = hmac.new(
        settings.AUTH_SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None
    return user_id

import hashlib
import hmac
import time
import os
from typing import Optional
from fastapi import HTTPException, status, Request
from app.database import get_db_engine
from app.models import User

SECRET_KEY = os.environ.get("SESSION_SECRET", "kvcell_secret_key_change_in_production_2026")

def hash_password(password: str) -> str:
    salt = "kvcell_salt_2026"
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def create_session_token(username: str, unit: str, role: str) -> str:
    expires = int(time.time()) + (86400 * 7)  # 7 days
    data = f"{username}:{unit}:{role}:{expires}"
    signature = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hex()
    return f"{data}:{signature}"

def verify_session_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return None
        username, unit, role, expires_str, sig = parts
        if int(expires_str) < time.time():
            return None
        data = f"{username}:{unit}:{role}:{expires_str}"
        expected_sig = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hex()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        return {"username": username, "unit": unit, "role": role}
    except Exception:
        return None

def bootstrap_initial_users():
    for unit, db_name in [("KVCELLLAGOS", "Lagos"), ("KVCELLMAGE", "Magé")]:
        engine, SessionLocal = get_db_engine(unit)
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == unit).first()
            if not user:
                default_user = User(
                    username=unit,
                    password_hash=hash_password("2023"),
                    name=f"Operador {db_name}",
                    role="admin",
                    unit=unit
                )
                db.add(default_user)
                db.commit()
        finally:
            db.close()

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Fake user database for auth (temporary for MVP)
# Using a function to avoid evaluation at import time
def get_fake_users_db():
    return {
        "citizen@example.com": {
            "email": "citizen@example.com",
            "full_name": "Citizen User",
            "hashed_password": get_password_hash("citizenpass"),
            "role": "citizen",
            "disabled": False,
        },
        "officer@example.com": {
            "email": "officer@example.com",
            "full_name": "Officer User",
            "hashed_password": get_password_hash("officerpass"),
            "role": "officer",
            "disabled": False,
        }
    }

def authenticate_user(fake_db, email: str, password: str):
    user = fake_db.get(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user
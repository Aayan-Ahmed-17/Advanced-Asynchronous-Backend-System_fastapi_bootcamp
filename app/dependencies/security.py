import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
SECRET_KEY_ACCESS = os.getenv("SECRET_KEY_ACCESS")
SECRET_KEY_REFRESH = os.getenv("SECRET_KEY_REFRESH")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Token Generation
def create_token(data: dict, secret: str, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, SECRET_KEY_ACCESS, delta, "access")

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, SECRET_KEY_REFRESH, delta, "refresh")

# Token Decoding Utilities
def decode_token(token: str, secret: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

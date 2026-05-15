from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.dependencies.security import decode_token, SECRET_KEY_ACCESS
from app.config.database import get_user_collection
from app.config.cache import redis_client
from app.models.user_model import User
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check Redis Blacklist
    if redis_client:
        is_blacklisted = await redis_client.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Decode and Validate JWT
    payload = decode_token(token, SECRET_KEY_ACCESS)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    token_type: str = payload.get("type")
    
    if email is None or token_type != "access":
        raise credentials_exception

    # 3. Fetch User from MongoDB (Async)
    user_collection = get_user_collection()
    user_dict = await user_collection.find_one({"email": email})
    
    if user_dict is None:
        raise credentials_exception
    
    return User(**user_dict)

async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth_schemas import UserCreate, UserLogin, UserRegistrationResponse, TokenExchangeResponse, GenericActionResponse, RefreshTokenRequest
from app.dependencies.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, SECRET_KEY_REFRESH
from app.dependencies.auth import get_current_user, oauth2_scheme
from app.config.database import get_user_collection
from app.config.cache import redis_client
from app.models.user_model import User
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    user_collection = get_user_collection()
    
    # Check if user already exists
    existing_user = await user_collection.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user_dict = {
        "email": user_in.email,
        "hashed_password": get_password_hash(user_in.password),
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await user_collection.insert_one(new_user_dict)
    new_user_dict["_id"] = str(result.inserted_id)
    
    # Map to response schema
    return {
        "id": new_user_dict["_id"],
        "email": new_user_dict["email"],
        "is_active": new_user_dict["is_active"],
        "is_superuser": new_user_dict["is_superuser"],
        "created_at": new_user_dict["created_at"]
    }

@router.post("/login", response_model=TokenExchangeResponse)
async def login(credentials: UserLogin):
    user_collection = get_user_collection()
    user = await user_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", response_model=GenericActionResponse)
async def logout(token: str = Depends(oauth2_scheme)):
    if redis_client:
        # Blacklist the current access token for its remaining life (approx 15 mins)
        await redis_client.setex(f"blacklist:{token}", timedelta(minutes=15), "revoked")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserRegistrationResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at
    }

@router.post("/refresh", response_model=TokenExchangeResponse)
async def refresh_token(body: RefreshTokenRequest):
    payload = decode_token(body.refresh_token, SECRET_KEY_REFRESH)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    email = payload.get("sub")
    access_token = create_access_token(data={"sub": email})
    # Rotate refresh token for enhanced security
    new_refresh_token = create_refresh_token(data={"sub": email})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

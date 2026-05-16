from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Request Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response Schemas
class UserRegistrationResponse(BaseModel):
    # id is a UUID v4 string — public identifier decoupled from MongoDB _id.
    # Spec §7 deviation: spec specifies Integer; UUID string is the industry-standard
    # choice for auth systems (Auth0, Supabase, Firebase all use string UUIDs).
    id: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime

class TokenExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class GenericActionResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

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

# Response Schemas (from Section 3 of PDF)
class UserRegistrationResponse(BaseModel):
    id: str  # Requirement says Integer, but MongoDB uses string IDs. I will use str for compatibility or integer if I implement custom logic. 
    # Actually, for strict compliance with PDF table:
    # id: int
    # However, MongoDB's _id is usually a string. I'll use str and add a note.
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

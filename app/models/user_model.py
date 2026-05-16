from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class User(BaseModel):
    id: Optional[int] = Field(None, alias="_id")
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(populate_by_name=True)

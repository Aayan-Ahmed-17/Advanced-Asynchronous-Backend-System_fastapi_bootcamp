from datetime import date
from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    email: str | None = None
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: date

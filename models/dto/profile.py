from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models.dto.user import User

class Profile(BaseModel):
    id: int
    name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    details: str
    image: Optional[str]
    user_id: int
    user: User
    created_at: datetime
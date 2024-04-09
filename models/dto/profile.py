from datetime import datetime
from pydantic import BaseModel
from models.dto.user import User

class Profile(BaseModel):
    id: int
    details: str
    user_id: int
    user: User
    created_at: datetime
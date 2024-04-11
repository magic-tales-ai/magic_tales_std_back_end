from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models.dto.profile import Profile


class Story(BaseModel):
    id: int
    profile_id: int
    session_id: str
    profile: Profile
    title: str
    features: Optional[str]
    synopsis: Optional[str]
    last_successful_step: Optional[int]
    created_at: datetime
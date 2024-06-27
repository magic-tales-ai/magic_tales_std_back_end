from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models.dto.profile import Profile


class Story(BaseModel):
    id: int
    profile_id: int
    ws_session_uid: str
    image: Optional[str]
    profile: Profile
    title: Optional[str]
    features: Optional[str]
    synopsis: Optional[str]
    last_successful_step: Optional[int]
    created_at: datetime
from pydantic import BaseModel, Field
from typing import Optional


class StoryAPI(BaseModel):
    id: Optional[str] = Field(None)
    profile_id: int
    title: str
    features: str
    synopsis: str
    last_successful_step: int

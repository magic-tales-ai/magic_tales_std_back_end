from pydantic import BaseModel, Field
from typing import Optional

class ProfileAPI(BaseModel):
    id: Optional[str] = Field(None)
    user_id: int
    details: str
from pydantic import BaseModel, Field
from typing import Optional

class UserAPI(BaseModel):
    id: int
    username: str
    email: str
    token: Optional[str] = Field(None)
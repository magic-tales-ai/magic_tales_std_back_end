from pydantic import BaseModel, Field
from typing import Optional

class RegisterAPI(BaseModel):
    id: Optional[int] = Field(None)
    username: str
    email: str
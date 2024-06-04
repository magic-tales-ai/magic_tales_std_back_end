from pydantic import BaseModel, Field
from typing import Optional


class RegisterAPI(BaseModel):
    id: Optional[int] = Field(None)
    name: str
    last_name: str
    username: str
    email: str
    language: str

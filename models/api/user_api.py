from pydantic import BaseModel, Field
from typing import Optional


class UserAPI(BaseModel):
    id: int
    name: Optional[str] # TODO: This will need to change when first version will launch. The field isn't Optional
    last_name: Optional[str] # TODO: This will need to change when first version will launch. The field isn't Optional
    username: str
    email: str
    token: Optional[str] = Field(None)
    image: Optional[str]

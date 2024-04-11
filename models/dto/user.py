from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models.dto.plan import Plan

class User(BaseModel):
    id: int
    name: Optional[str] # TODO: This will need to change when first version will launch. The field isn't Optional
    last_name: Optional[str] # TODO: This will need to change when first version will launch. The field isn't Optional
    username: str
    email: str
    active: bool
    plan_id: int
    plan: Plan
    assistant_id: Optional[str]
    created_at: datetime
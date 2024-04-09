from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from models.dto.plan import Plan

class User(BaseModel):
    id: int
    username: str
    email: str
    plan_id: int
    plan: Plan
    assistant_id: Optional[str]
    created_at: datetime
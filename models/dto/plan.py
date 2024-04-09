
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Plan(BaseModel):
    id: int
    name: str
    image: str
    is_popular: bool
    price: float
    discount_per_year: Optional[float]
    save_up_message: Optional[str]
    stories_per_month: Optional[int]
    customization_options: Optional[str]
    voice_synthesis: Optional[str]
    custommer_support: Optional[str]
    description: Optional[dict]
    created_at: datetime
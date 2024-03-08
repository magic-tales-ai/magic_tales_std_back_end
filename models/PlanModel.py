from pydantic import BaseModel
from typing import List, Optional

class PlanModel(BaseModel):
    id: int
    name: str
    image: str
    is_popular: bool
    price: float
    discount_per_year: Optional[float]
    save_up_message: Optional[str]
    stories_per_month: int
    customization_options: Optional[str] = None
    voice_synthesis: Optional[str] = None
    custommer_support: Optional[str] = None
    description: List[str]
    
    def __init__(self, id, name, image, is_popular, price, discount_per_year, save_up_message, stories_per_month, customization_options, voice_synthesis, custommer_support, description):
        super().__init__(
            id = id, 
            image = image, 
            name = name, 
            is_popular = is_popular,
            price = price, 
            discount_per_year = discount_per_year,
            save_up_message = save_up_message,
            stories_per_month = stories_per_month, 
            customization_options = customization_options, 
            voice_synthesis = voice_synthesis, 
            custommer_support = custommer_support, 
            description = description
        )
        self.id = id
        self.image = image
        self.name = name
        self.is_popular = is_popular
        self.price = price
        self.discount_per_year = discount_per_year
        self.save_up_message = save_up_message
        self.stories_per_month = stories_per_month
        self.customization_options = customization_options
        self.voice_synthesis = voice_synthesis
        self.custommer_support = custommer_support
        self.description = description
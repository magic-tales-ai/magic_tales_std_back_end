from db import Base
from sqlalchemy import Column, Integer, JSON, Float, Text, Boolean, TIMESTAMP
from datetime import datetime


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    image = Column(Text)
    is_popular = Column(Boolean)
    price = Column(Float)
    discount_per_year = Column(Text)
    save_up_message = Column(Text)
    stories_per_month = Column(Integer)
    customization_options = Column(Text)
    voice_synthesis = Column(Text)
    custommer_support = Column(Text)
    description = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

from db import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from datetime import datetime

class Story(Base):
    __tablename__ = 'stories'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer)
    title = Column(Text)
    synopsis = Column(Text)
    last_successful_step = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
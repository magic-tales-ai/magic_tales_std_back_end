from db import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from datetime import datetime
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True)
    profile_id = Column(ForeignKey("profiles.id"))
    profile = relationship("Profile", lazy="joined")
    title = Column(Text)
    features = Column(Text)
    synopsis = Column(Text)
    last_successful_step = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

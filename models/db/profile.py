from db import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    details = Column(Text)
    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", lazy="joined")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

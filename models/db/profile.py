import datetime
from db import Base
from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields
from marshmallow.fields import Nested


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    details = Column(Text)
    user_id = Column(ForeignKey("users.id"))
    user = relationship("User", lazy="joined")
    created_at = Column(TIMESTAMP, default=datetime.datetime.now(datetime.UTC))

    def to_dict(self):
        return {
            "id": self.id,
            "details": self.details,
            "user_id": self.user_id,
            "user": self.user.to_dict(),
            "created_at": self.created_at,
        }
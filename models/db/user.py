from db import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255)) # TODO: This will need to change when first version will launch. The field isn't Nullable
    last_name = Column(String(255))# TODO: This will need to change when first version will launch. The field isn't Nullable
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    new_email = Column(String(255))
    new_password = Column(String(255))
    validation_code = Column(Integer)
    active = Column(Boolean, nullable=False, default=0)
    plan_id = Column(ForeignKey("plans.id"))
    plan = relationship("Plan", lazy="joined")
    assistant_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # This field is ONLY for mapping to the DTO model. If this field doesn't exist here, the automatic mapping doesn't work.
    image = None

    def __str__(self):
        return f"User info: username='{self.username}', email='{self.email}', created_at='{self.created_at}')"

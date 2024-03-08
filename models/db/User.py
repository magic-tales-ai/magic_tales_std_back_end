from db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    plan_id = Column(ForeignKey('plans.id'))
    plan = relationship('Plan', lazy='joined')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
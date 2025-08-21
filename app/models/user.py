# models/user.py
from sqlalchemy import Column, Integer, String
from app.models.base import Base, TimestampMixin
from sqlalchemy.orm import relationship


class User(Base, TimestampMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    timezone = Column(String(50), default="Asia/Seoul", nullable=False)  # 시간대

    # 관계 설정
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', timezone='{self.timezone}')>"

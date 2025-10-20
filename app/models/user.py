from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True, comment="사용자 이름")
    hashed_password = Column(String(255), nullable=False, comment="해쉬된 비밀번호")

    questions = relationship("Question", back_populates="author")
    answers = relationship("Answer", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

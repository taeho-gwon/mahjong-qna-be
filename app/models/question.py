from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    title = Column(String(200), nullable=False, index=True, comment="질문 제목")
    content = Column(Text, nullable=False, comment="질문 내용")

    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="작성자 ID",
    )
    author = relationship("User", back_populates="questions")

    def __repr__(self):
        return (
            f"<Question(id={self.id}, title='{self.title[:30]}...', author_id='{self.author_id}')>"
        )

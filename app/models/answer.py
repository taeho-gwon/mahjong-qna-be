from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Answer(Base):
    __tablename__ = "answers"

    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="질문 ID",
    )

    content = Column(Text, nullable=False, comment="답변 내용")

    author_nickname = Column(String(50), nullable=False, comment="작성자 닉네임")

    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return (
            f"<Answer("
            f"id={self.id}, "
            f"question_id={self.question_id}, "
            f"author='{self.author_nickname}')>"
        )

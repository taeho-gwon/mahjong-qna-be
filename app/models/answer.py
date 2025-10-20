from sqlalchemy import Column, ForeignKey, Integer, Text
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

    question = relationship("Question", back_populates="answers")

    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="작성자 ID",
    )

    def __repr__(self):
        return (
            f"<Answer(id={self.id}, question_id={self.question_id}, author_id='{self.author_id}')>"
        )

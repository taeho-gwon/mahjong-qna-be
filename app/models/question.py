from sqlalchemy import Column, String, Text

from app.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    title = Column(String(200), nullable=False, index=True, comment="질문 제목")
    content = Column(Text, nullable=False, comment="질문 내용")
    author_nickname = Column(String(50), nullable=False, comment="작성자 닉네임")

    def __repr__(self):
        return (
            f"<Question("
            f"id={self.id}, "
            f"title='{self.title[:30]}...', "
            f"author='{self.author_nickname}')>"
        )

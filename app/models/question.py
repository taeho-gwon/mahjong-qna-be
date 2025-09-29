from sqlalchemy import Column, String, Text

from app.models.base import Base


class Question(Base):
    """질문 모델

    마작 관련 질문을 저장하는 테이블입니다.
    """
    __tablename__ = "questions"

    # 기본 정보
    title = Column(String(200), nullable=False, index=True, comment="질문 제목")
    content = Column(Text, nullable=False, comment="질문 내용")

    # 작성자 정보 (인증 전이므로 닉네임만)
    author_nickname = Column(String(50), nullable=False, comment="작성자 닉네임")

    def __repr__(self):
        return f"<Question(id={self.id}, title='{self.title[:30]}...', author='{self.author_nickname}')>"
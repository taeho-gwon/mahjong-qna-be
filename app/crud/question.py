from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.schemas.question import QuestionCreate


async def create_question(db: AsyncSession, question_in: QuestionCreate) -> Question:
    question_dict = question_in.model_dump()
    db_question = Question(**question_dict)
    db.add(db_question)
    await db.commit()
    return db_question

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.schemas.question import QuestionCreate


async def create_question(db: AsyncSession, question_in: QuestionCreate) -> Question:
    question_dict = question_in.model_dump()
    db_question = Question(**question_dict)
    db.add(db_question)
    await db.commit()
    return db_question


async def read_question_by_id(db: AsyncSession, question_id: int) -> Question | None:
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def read_questions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
) -> tuple[list[Question], int]:
    # 전체 개수 조회
    count_query = select(func.count()).select_from(Question)
    total = await db.scalar(count_query)

    # 질문 목록 조회 (최신순)
    query = select(Question).order_by(Question.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()

    return list(questions), total or 0

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate


async def create_question(db: AsyncSession, question_in: QuestionCreate) -> Question:
    question_dict = question_in.model_dump()
    question = Question(**question_dict)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def read_question_by_id(db: AsyncSession, question_id: int) -> Question | None:
    result = await db.execute(select(Question).where(Question.id == question_id))
    return result.scalar_one_or_none()


async def read_questions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
) -> tuple[list[Question], int]:
    count_query = select(func.count()).select_from(Question)
    total = await db.scalar(count_query)

    query = select(Question).order_by(Question.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()

    return list(questions), total or 0


async def update_question(
    db: AsyncSession,
    question_id: int,
    question_in: QuestionUpdate,
) -> Question | None:
    question = await read_question_by_id(db, question_id)
    if question is None:
        return None

    update_data = question_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(question, field, value)

    await db.commit()
    await db.refresh(question)
    return question

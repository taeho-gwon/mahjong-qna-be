from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer import Answer
from app.schemas.answer import AnswerCreate, AnswerUpdate


async def create_answer(
    db: AsyncSession,
    question_id: int,
    answer_in: AnswerCreate,
) -> Answer:
    answer_dict = answer_in.model_dump()
    answer_dict["question_id"] = question_id

    answer = Answer(**answer_dict)
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def read_answer_by_id(db: AsyncSession, answer_id: int) -> Answer | None:
    result = await db.execute(select(Answer).where(Answer.id == answer_id))
    return result.scalar_one_or_none()


async def read_answers_by_question_id(
    db: AsyncSession,
    question_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Answer], int]:
    count_query = select(func.count()).select_from(Answer).where(Answer.question_id == question_id)
    total = await db.scalar(count_query)

    query = (
        select(Answer)
        .where(Answer.question_id == question_id)
        .order_by(Answer.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    answers = result.scalars().all()

    return list(answers), total or 0


async def update_answer(
    db: AsyncSession,
    answer_id: int,
    answer_in: AnswerUpdate,
) -> Answer | None:
    answer = await read_answer_by_id(db, answer_id)
    if answer is None:
        return None

    update_data = answer_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(answer, field, value)

    await db.commit()
    await db.refresh(answer)
    return answer


async def delete_answer(db: AsyncSession, answer_id: int) -> bool:
    answer = await read_answer_by_id(db, answer_id)
    if answer is None:
        return False

    await db.delete(answer)
    await db.commit()
    return True

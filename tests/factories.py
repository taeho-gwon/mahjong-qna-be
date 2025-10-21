from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import create_answer
from app.crud.question import create_question
from app.crud.user import create_user
from app.models import Answer, Question, User
from app.schemas.answer import AnswerCreate
from app.schemas.question import QuestionCreate
from app.schemas.user import UserSignup


async def create_test_user(
    db: AsyncSession,
    username: str = "testuser",
    password: str = "testpass1234",
) -> User:
    user_in = UserSignup(username=username, password=password)
    user = await create_user(db, user_in)
    await db.flush()
    await db.refresh(user)
    return user


async def create_test_question(
    db: AsyncSession,
    author_id: int,
    title: str = "테스트 질문입니다",
    content: str = "이것은 테스트용 질문 내용입니다. 최소 10자 이상이어야 합니다.",
) -> Question:
    question_in = QuestionCreate(title=title, content=content)
    question = await create_question(db, question_in, author_id)
    await db.flush()
    await db.refresh(question)
    return question


async def create_test_answer(
    db: AsyncSession,
    question_id: int,
    author_id: int,
    content: str = "이것은 테스트용 답변 내용입니다. 최소 10자 이상이어야 합니다.",
) -> Answer:
    answer_in = AnswerCreate(content=content)
    answer = await create_answer(db, question_id, answer_in, author_id)
    await db.flush()
    await db.refresh(answer)
    return answer

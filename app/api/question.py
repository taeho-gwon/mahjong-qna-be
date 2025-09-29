from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import create_question
from app.db.database import get_session
from app.schemas.question import QuestionCreate, QuestionResponse


router = APIRouter(prefix="/questions", tags=["questions"])


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="질문 생성",
    description="새로운 마작 질문을 생성합니다.",
)
async def create_question_api(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_session),
) -> QuestionResponse:
    question = await create_question(db, question_in)
    return question
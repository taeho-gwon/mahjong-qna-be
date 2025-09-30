from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import create_question, read_question
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
async def create_question_handler(
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_session),
) -> QuestionResponse:
    return await create_question(db, question_in)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="질문 단일 조회",
    description="ID로 특정 질문을 조회합니다.",
)
async def get_question_handler(
    question_id: int,
    db: AsyncSession = Depends(get_session),
) -> QuestionResponse:
    question = await read_question(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"질문을 찾을 수 없습니다. (ID: {question_id})",
        )
    return question

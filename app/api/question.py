from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import create_question, read_question_by_id, read_questions, update_question
from app.db.database import get_session
from app.schemas.question import (
    PaginationMeta,
    QuestionCreate,
    QuestionListItem,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdate,
)


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
    question = await read_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"질문을 찾을 수 없습니다. (ID: {question_id})",
        )
    return question


@router.get(
    "",
    response_model=QuestionListResponse,
    status_code=status.HTTP_200_OK,
    summary="질문 목록 조회",
    description="질문 목록을 페이지네이션과 함께 조회합니다. 최신순으로 정렬됩니다.",
)
async def list_questions_handler(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(default=10, ge=1, le=100, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_session),
) -> QuestionListResponse:
    skip = (page - 1) * size

    questions, total = await read_questions(db, skip=skip, limit=size)

    total_pages = ceil(total / size) if total > 0 else 0

    return QuestionListResponse(
        items=[QuestionListItem.model_validate(q) for q in questions],
        pagination=PaginationMeta(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        ),
    )


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="질문 수정",
    description="ID로 특정 질문을 수정합니다. 제공된 필드만 업데이트됩니다.",
)
async def update_question_handler(
    question_id: int,
    question_in: QuestionUpdate,
    db: AsyncSession = Depends(get_session),
) -> QuestionResponse:
    question = await update_question(db, question_id, question_in)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"질문을 찾을 수 없습니다. (ID: {question_id})",
        )
    return question

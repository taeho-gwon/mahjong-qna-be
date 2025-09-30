from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import (
    create_answer,
    delete_answer,
    read_answer_by_id,
    read_answers_by_question_id,
    update_answer,
)
from app.crud.question import read_question_by_id
from app.db.database import get_session
from app.schemas.answer import (
    AnswerCreate,
    AnswerListItem,
    AnswerResponse,
    AnswerUpdate,
)


router = APIRouter(prefix="/questions/{question_id}/answers", tags=["answers"])


@router.post(
    "",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="답변 생성",
    description="특정 질문에 대한 답변을 생성합니다.",
)
async def create_answer_handler(
    question_id: int,
    answer_in: AnswerCreate,
    db: AsyncSession = Depends(get_session),
) -> AnswerResponse:
    question = await read_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"질문을 찾을 수 없습니다. (ID: {question_id})",
        )

    answer = await create_answer(db, question_id, answer_in)
    return AnswerResponse.model_validate(answer)


@router.get(
    "",
    response_model=list[AnswerListItem],
    status_code=status.HTTP_200_OK,
    summary="답변 목록 조회",
    description="특정 질문의 모든 답변을 조회합니다. 최신순으로 정렬됩니다.",
)
async def list_answers_handler(
    question_id: int,
    skip: int = Query(default=0, ge=0, description="건너뛸 개수"),
    limit: int = Query(default=100, ge=1, le=100, description="가져올 최대 개수"),
    db: AsyncSession = Depends(get_session),
) -> list[AnswerListItem]:
    question = await read_question_by_id(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"질문을 찾을 수 없습니다. (ID: {question_id})",
        )

    answers, _ = await read_answers_by_question_id(db, question_id, skip, limit)
    return [AnswerListItem.model_validate(a) for a in answers]


@router.get(
    "/{answer_id}",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="답변 단일 조회",
    description="ID로 특정 답변을 조회합니다.",
)
async def get_answer_handler(
    question_id: int,
    answer_id: int,
    db: AsyncSession = Depends(get_session),
) -> AnswerResponse:
    answer = await read_answer_by_id(db, answer_id)

    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"답변을 찾을 수 없습니다. (ID: {answer_id})",
        )

    if answer.question_id != question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"답변이 해당 질문에 속하지 않습니다."
            f"(질문 ID: {question_id}, 답변 ID: {answer_id})",
        )

    return AnswerResponse.model_validate(answer)


@router.patch(
    "/{answer_id}",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="답변 수정",
    description="ID로 특정 답변을 수정합니다. 제공된 필드만 업데이트됩니다.",
)
async def update_answer_handler(
    question_id: int,
    answer_id: int,
    answer_in: AnswerUpdate,
    db: AsyncSession = Depends(get_session),
) -> AnswerResponse:
    existing_answer = await read_answer_by_id(db, answer_id)

    if existing_answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"답변을 찾을 수 없습니다. (ID: {answer_id})",
        )

    if existing_answer.question_id != question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"답변이 해당 질문에 속하지 않습니다."
            f"(질문 ID: {question_id}, 답변 ID: {answer_id})",
        )

    answer = await update_answer(db, answer_id, answer_in)
    return AnswerResponse.model_validate(answer)


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="답변 삭제",
    description="ID로 특정 답변을 삭제합니다. 성공 시 204 No Content를 반환합니다.",
)
async def delete_answer_handler(
    question_id: int,
    answer_id: int,
    db: AsyncSession = Depends(get_session),
) -> None:
    existing_answer = await read_answer_by_id(db, answer_id)

    if existing_answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"답변을 찾을 수 없습니다. (ID: {answer_id})",
        )

    if existing_answer.question_id != question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"답변이 해당 질문에 속하지 않습니다."
            f"(질문 ID: {question_id}, 답변 ID: {answer_id})",
        )

    await delete_answer(db, answer_id)
